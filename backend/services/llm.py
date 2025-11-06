"""
LLM API 통합 서비스
OpenAI 및 Anthropic Claude API 호출 관리
"""
from typing import Optional, Dict, Any
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from backend.core.config import settings
from backend.core.logging import logger
import asyncio


class LLMService:
    """LLM API 호출 서비스"""

    def __init__(self):
        self.openai_client: Optional[AsyncOpenAI] = None
        self.anthropic_client: Optional[AsyncAnthropic] = None
        self._initialize_clients()

    def _initialize_clients(self):
        """API 클라이언트 초기화"""
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI client initialized")

        if settings.ANTHROPIC_API_KEY:
            self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            logger.info("Anthropic client initialized")

        if not self.openai_client and not self.anthropic_client:
            logger.warning("No LLM API keys configured")

    async def chat_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        provider: str = "openai"
    ) -> str:
        """
        LLM 채팅 완성 요청

        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트
            model: 모델 이름
            temperature: 온도 (0.0 - 1.0)
            max_tokens: 최대 토큰 수
            provider: 'openai' 또는 'anthropic'

        Returns:
            LLM 응답 텍스트
        """
        try:
            if provider == "openai":
                return await self._openai_chat(
                    prompt, system_prompt, model, temperature, max_tokens
                )
            elif provider == "anthropic":
                return await self._anthropic_chat(
                    prompt, system_prompt, model, temperature, max_tokens
                )
            else:
                raise ValueError(f"Unsupported provider: {provider}")

        except Exception as e:
            logger.error(f"LLM API call failed: {e}")
            raise

    async def _openai_chat(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """OpenAI API 호출"""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self.openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content or ""

    async def _anthropic_chat(
        self,
        prompt: str,
        system_prompt: Optional[str],
        model: str,
        temperature: float,
        max_tokens: int
    ) -> str:
        """Anthropic Claude API 호출"""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")

        # Claude 모델 매핑
        claude_model = model.replace("gpt-", "claude-")
        if not claude_model.startswith("claude-"):
            claude_model = "claude-3-5-sonnet-20241022"

        response = await self.anthropic_client.messages.create(
            model=claude_model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    async def batch_completion(
        self,
        prompts: list[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> list[str]:
        """
        배치 LLM 요청

        Args:
            prompts: 프롬프트 리스트
            system_prompt: 공통 시스템 프롬프트
            **kwargs: chat_completion 파라미터

        Returns:
            응답 텍스트 리스트
        """
        tasks = [
            self.chat_completion(prompt, system_prompt, **kwargs)
            for prompt in prompts
        ]
        return await asyncio.gather(*tasks)


# 전역 LLM 서비스 인스턴스
llm_service = LLMService()
