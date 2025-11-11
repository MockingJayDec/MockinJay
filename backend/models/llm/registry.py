"""
LLM Model Registry
모델 등록 및 팩토리 패턴
"""
from typing import Dict, Type, Optional
from backend.models.llm.base_llm import BaseLLM
from backend.models.llm.openai_llm import OpenAILLM
import logging

logger = logging.getLogger(__name__)


class LLMRegistry:
    """
    LLM 모델 레지스트리
    설정 기반으로 모델을 동적으로 로드
    """

    _models: Dict[str, Type[BaseLLM]] = {
        "gpt-4o": OpenAILLM,
        "gpt-4o-mini": OpenAILLM,
        "gpt-4-turbo": OpenAILLM,
        "gpt-4": OpenAILLM,
        "gpt-3.5-turbo": OpenAILLM,
        # 추후 추가할 모델들:
        # "claude-3-5-sonnet": AnthropicLLM,
        # "gemini-pro": GeminiLLM,
        # "llama-3-8b": LlamaLLM,
    }

    @classmethod
    def register(cls, name: str, llm_class: Type[BaseLLM]):
        """
        새로운 LLM 모델 등록

        Args:
            name: 모델 식별자
            llm_class: BaseLLM을 상속한 클래스
        """
        if not issubclass(llm_class, BaseLLM):
            raise TypeError(f"{llm_class} must inherit from BaseLLM")

        cls._models[name] = llm_class
        logger.info(f"Registered LLM model: {name}")

    @classmethod
    def get(cls, model_name: str, **kwargs) -> BaseLLM:
        """
        LLM 모델 인스턴스 생성

        Args:
            model_name: 등록된 모델 이름
            **kwargs: 모델별 설정 파라미터

        Returns:
            BaseLLM 인스턴스

        Raises:
            ValueError: 등록되지 않은 모델인 경우
        """
        if model_name not in cls._models:
            available = list(cls._models.keys())
            raise ValueError(
                f"Unknown LLM model: {model_name}. "
                f"Available models: {available}"
            )

        llm_class = cls._models[model_name]

        # 모델 이름을 kwargs에 추가
        if "model_name" not in kwargs:
            kwargs["model_name"] = model_name

        return llm_class(**kwargs)

    @classmethod
    def list_models(cls) -> Dict[str, str]:
        """
        등록된 모든 모델 목록

        Returns:
            {모델명: 클래스명} 딕셔너리
        """
        return {
            name: llm.__name__
            for name, llm in cls._models.items()
        }
