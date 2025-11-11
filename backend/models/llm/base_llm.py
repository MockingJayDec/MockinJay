"""
Base abstract class for LLM models
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """
    추상 LLM 클래스
    모든 LLM 모델은 이 인터페이스를 구현해야 합니다.
    """

    def __init__(self, model_name: str, **kwargs):
        self.model_name = model_name
        self.config = kwargs
        logger.info(f"Initializing {self.__class__.__name__} with model: {model_name}")

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> str:
        """
        텍스트 완성 생성

        Args:
            prompt: 사용자 프롬프트
            system_prompt: 시스템 프롬프트 (선택)
            temperature: 샘플링 온도 (0.0 - 1.0)
            max_tokens: 최대 토큰 수
            **kwargs: 모델별 추가 파라미터

        Returns:
            생성된 텍스트
        """
        pass

    @abstractmethod
    async def classify(
        self,
        text: str,
        labels: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        텍스트 분류

        Args:
            text: 분류할 텍스트
            labels: 가능한 레이블 리스트
            system_prompt: 시스템 프롬프트 (선택)
            **kwargs: 모델별 추가 파라미터

        Returns:
            {"label": str, "confidence": float, "reasoning": str}
        """
        pass

    @property
    @abstractmethod
    def context_window(self) -> int:
        """모델의 컨텍스트 윈도우 크기"""
        pass

    @property
    def name(self) -> str:
        """모델 이름"""
        return self.model_name

    def get_metadata(self) -> Dict[str, Any]:
        """
        모델 메타데이터 반환

        Returns:
            모델 정보 딕셔너리
        """
        return {
            "name": self.name,
            "context_window": self.context_window,
            "class": self.__class__.__name__,
            "config": self.config
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model={self.model_name})"
