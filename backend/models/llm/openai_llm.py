"""
OpenAI LLM implementation
"""
from typing import Dict, Any, Optional, List
from openai import AsyncOpenAI
from backend.models.llm.base_llm import BaseLLM
from backend.core.config import settings
import logging
import json

logger = logging.getLogger(__name__)


class OpenAILLM(BaseLLM):
    """
    OpenAI API를 사용하는 LLM
    GPT-4, GPT-4o, GPT-3.5-turbo 등
    """

    CONTEXT_WINDOWS = {
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
        "gpt-4-turbo": 128000,
        "gpt-4": 8192,
        "gpt-3.5-turbo": 16385,
    }

    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        **kwargs
    ):
        super().__init__(model_name=model_name, **kwargs)

        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key is required")

        self.client = AsyncOpenAI(api_key=self.api_key)
        logger.info(f"OpenAI client initialized with model: {model_name}")

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """텍스트 완성 생성"""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    async def classify(
        self,
        text: str,
        labels: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """텍스트 분류"""
        if not system_prompt:
            system_prompt = f"""You are a text classifier.
Classify the given text into one of these categories: {', '.join(labels)}
Respond in JSON format: {{"label": "...", "confidence": 0.0-1.0, "reasoning": "..."}}"""

        response_text = await self.complete(
            prompt=text,
            system_prompt=system_prompt,
            temperature=0.3,  # 분류는 낮은 온도 사용
            **kwargs
        )

        try:
            # JSON 파싱
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse JSON response: {response_text}")
            # 기본 응답 반환
            return {
                "label": labels[0],
                "confidence": 0.5,
                "reasoning": "Failed to parse model response"
            }

    @property
    def context_window(self) -> int:
        """모델의 컨텍스트 윈도우 크기"""
        return self.CONTEXT_WINDOWS.get(self.model_name, 4096)
