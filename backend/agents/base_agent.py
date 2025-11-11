"""
Base abstract class for all agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from backend.models.llm.registry import LLMRegistry
from backend.models.llm.base_llm import BaseLLM
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    추상 Agent 클래스
    모든 전문화된 Agent는 이 클래스를 상속받습니다.
    """

    def __init__(
        self,
        agent_name: str,
        llm_model: Optional[str] = None,
        **kwargs
    ):
        self.agent_name = agent_name
        self.config = kwargs

        # LLM 초기화 (필요한 경우)
        self.llm: Optional[BaseLLM] = None
        if llm_model:
            try:
                self.llm = LLMRegistry.get(llm_model)
                logger.info(f"{agent_name} initialized with LLM: {llm_model}")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM for {agent_name}: {e}")

        # Agent가 사용하는 도구들
        self.tools: List[Any] = []

        logger.info(f"Agent initialized: {agent_name}")

    @abstractmethod
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Agent의 핵심 실행 로직

        Args:
            input_data: 입력 데이터 딕셔너리

        Returns:
            실행 결과 딕셔너리
        """
        pass

    async def think(self, context: Dict[str, Any]) -> str:
        """
        Agent의 사고 과정 (LLM 활용)

        Args:
            context: 사고를 위한 컨텍스트

        Returns:
            사고 결과 텍스트
        """
        if not self.llm:
            return "No LLM available for thinking"

        prompt = self._build_thinking_prompt(context)
        try:
            result = await self.llm.complete(prompt=prompt, temperature=0.7)
            return result
        except Exception as e:
            logger.error(f"Thinking failed for {self.agent_name}: {e}")
            return f"Thinking error: {str(e)}"

    def _build_thinking_prompt(self, context: Dict[str, Any]) -> str:
        """
        사고 프롬프트 생성 (서브클래스에서 오버라이드 가능)

        Args:
            context: 컨텍스트 정보

        Returns:
            프롬프트 문자열
        """
        return f"Analyze the following context and provide insights: {context}"

    def add_tool(self, tool: Any):
        """Agent에 도구 추가"""
        self.tools.append(tool)
        logger.info(f"Tool added to {self.agent_name}: {tool}")

    def get_metadata(self) -> Dict[str, Any]:
        """
        Agent 메타데이터 반환

        Returns:
            Agent 정보 딕셔너리
        """
        return {
            "name": self.agent_name,
            "class": self.__class__.__name__,
            "llm": self.llm.name if self.llm else None,
            "tools_count": len(self.tools),
            "config": self.config
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.agent_name})"
