"""
Orchestrator Agent - 전체 워크플로우 조율
"""
from typing import Dict, Any, List, Optional
from backend.agents.base_agent import BaseAgent
import logging
import asyncio

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    여러 Agent들을 조율하는 메인 오케스트레이터
    전체 파이프라인 실행 흐름을 관리
    """

    def __init__(self, strategy: str = "sequential"):
        """
        Args:
            strategy: 실행 전략 ("sequential" 또는 "parallel")
        """
        self.strategy = strategy
        self.agents: List[BaseAgent] = []
        logger.info(f"Orchestrator initialized with strategy: {strategy}")

    def register_agent(self, agent: BaseAgent, priority: int = 0):
        """
        Agent 등록

        Args:
            agent: 등록할 Agent
            priority: 우선순위 (낮을수록 먼저 실행)
        """
        self.agents.append({"agent": agent, "priority": priority})
        # 우선순위 순으로 정렬
        self.agents.sort(key=lambda x: x["priority"])
        logger.info(f"Agent registered: {agent.agent_name} (priority: {priority})")

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        전체 파이프라인 실행

        Args:
            input_data: 초기 입력 데이터

        Returns:
            최종 실행 결과
        """
        logger.info(f"Starting orchestration with strategy: {self.strategy}")

        if self.strategy == "sequential":
            return await self._execute_sequential(input_data)
        elif self.strategy == "parallel":
            return await self._execute_parallel(input_data)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    async def _execute_sequential(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        순차 실행: 각 Agent가 이전 Agent의 출력을 입력으로 받음

        Args:
            input_data: 초기 입력

        Returns:
            최종 결과
        """
        current_data = input_data.copy()
        results = {}

        for agent_info in self.agents:
            agent = agent_info["agent"]
            logger.info(f"Executing agent: {agent.agent_name}")

            try:
                result = await agent.execute(current_data)
                results[agent.agent_name] = result

                # 다음 Agent를 위해 현재 결과 병합
                current_data.update(result)

            except Exception as e:
                logger.error(f"Agent {agent.agent_name} failed: {e}")
                results[agent.agent_name] = {"error": str(e)}

        return {
            "strategy": "sequential",
            "agent_results": results,
            "final_output": current_data
        }

    async def _execute_parallel(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        병렬 실행: 모든 Agent가 동일한 입력을 받고 독립적으로 실행

        Args:
            input_data: 입력 데이터

        Returns:
            모든 Agent의 결과 집합
        """
        tasks = []

        for agent_info in self.agents:
            agent = agent_info["agent"]
            logger.info(f"Scheduling agent: {agent.agent_name}")
            tasks.append(self._execute_agent_safe(agent, input_data))

        # 모든 Agent 동시 실행
        agent_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 결과 정리
        results = {}
        for agent_info, result in zip(self.agents, agent_results):
            agent_name = agent_info["agent"].agent_name
            if isinstance(result, Exception):
                logger.error(f"Agent {agent_name} failed: {result}")
                results[agent_name] = {"error": str(result)}
            else:
                results[agent_name] = result

        return {
            "strategy": "parallel",
            "agent_results": results
        }

    async def _execute_agent_safe(
        self,
        agent: BaseAgent,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Agent 실행 래퍼 (에러 핸들링)

        Args:
            agent: 실행할 Agent
            input_data: 입력 데이터

        Returns:
            Agent 실행 결과
        """
        try:
            return await agent.execute(input_data)
        except Exception as e:
            logger.error(f"Agent {agent.agent_name} execution failed: {e}")
            raise

    def list_agents(self) -> List[Dict[str, Any]]:
        """
        등록된 모든 Agent 목록

        Returns:
            Agent 정보 리스트
        """
        return [
            {
                "name": agent_info["agent"].agent_name,
                "priority": agent_info["priority"],
                "class": agent_info["agent"].__class__.__name__
            }
            for agent_info in self.agents
        ]
