"""
성능 모니터링 및 최적화 서비스
"""
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from backend.services.cache import cache_service

logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    성능 측정 및 모니터링 서비스
    - 응답 시간 추적 (P50, P95, P99)
    - 의도 분류 정확도 측정
    - 시스템 에러율 모니터링
    """

    def __init__(self):
        """모니터 초기화"""
        self.cache = cache_service
        self._reset_metrics()
        logger.info("Performance Monitor initialized")

    def _reset_metrics(self):
        """메트릭 초기화"""
        self.response_times: List[float] = []
        self.intent_predictions: List[Dict[str, Any]] = []
        self.error_count = 0
        self.total_requests = 0

    def record_response_time(
        self,
        response_time: float,
        intent: str,
        question: str
    ) -> None:
        """
        응답 시간 기록

        Args:
            response_time: 응답 시간 (초)
            intent: 분류된 의도
            question: 사용자 질문
        """
        self.response_times.append(response_time)
        self.total_requests += 1

        # Redis에도 저장 (7일간 유지) - Redis가 사용 가능한 경우에만
        if self.cache.redis_client is not None:
            try:
                cache_key = f"perf:response_time:{int(time.time())}"
                self.cache.redis_client.setex(
                    cache_key,
                    timedelta(days=7),
                    str(response_time)
                )
            except Exception as e:
                logger.warning(f"Failed to cache response time to Redis: {e}")

        logger.info(
            f"Response time recorded: {response_time:.2f}s "
            f"(intent: {intent}, total: {self.total_requests})"
        )

    def record_intent_prediction(
        self,
        question: str,
        predicted_intent: str,
        confidence: float,
        actual_intent: Optional[str] = None
    ) -> None:
        """
        의도 분류 결과 기록

        Args:
            question: 사용자 질문
            predicted_intent: 예측된 의도
            confidence: 신뢰도
            actual_intent: 실제 의도 (있을 경우)
        """
        prediction = {
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "predicted": predicted_intent,
            "confidence": confidence,
            "actual": actual_intent
        }

        self.intent_predictions.append(prediction)

        # Redis에도 저장 - Redis가 사용 가능한 경우에만
        if self.cache.redis_client is not None:
            try:
                cache_key = f"perf:intent:{int(time.time())}"
                self.cache.redis_client.setex(
                    cache_key,
                    timedelta(days=7),
                    str(prediction)
                )
            except Exception as e:
                logger.warning(f"Failed to cache intent prediction to Redis: {e}")

        logger.debug(f"Intent prediction recorded: {predicted_intent} ({confidence:.2f})")

    def record_error(self, error_type: str, error_message: str) -> None:
        """
        에러 기록

        Args:
            error_type: 에러 타입
            error_message: 에러 메시지
        """
        self.error_count += 1
        self.total_requests += 1

        # Redis에도 저장 - Redis가 사용 가능한 경우에만
        if self.cache.redis_client is not None:
            try:
                cache_key = f"perf:error:{int(time.time())}"
                self.cache.redis_client.setex(
                    cache_key,
                    timedelta(days=7),
                    f"{error_type}: {error_message}"
                )
            except Exception as e:
                logger.warning(f"Failed to cache error to Redis: {e}")

        logger.error(f"Error recorded: {error_type} - {error_message}")

    def get_response_time_percentiles(self) -> Dict[str, float]:
        """
        응답 시간 백분위수 계산

        Returns:
            P50, P95, P99 백분위수
        """
        if not self.response_times:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        sorted_times = sorted(self.response_times)
        n = len(sorted_times)

        # 백분위수 인덱스 계산 (0-based, 경계값 처리)
        def get_percentile_index(n: int, p: float) -> int:
            """백분위수 인덱스 계산 (0 <= p <= 1)"""
            if n == 0:
                return 0
            index = int(n * p)
            # 경계값 처리
            return min(index, n - 1)

        return {
            "p50": sorted_times[get_percentile_index(n, 0.50)] if n > 0 else 0.0,
            "p95": sorted_times[get_percentile_index(n, 0.95)] if n > 0 else 0.0,
            "p99": sorted_times[get_percentile_index(n, 0.99)] if n > 0 else 0.0,
            "mean": sum(sorted_times) / n if n > 0 else 0.0,
            "min": min(sorted_times) if n > 0 else 0.0,
            "max": max(sorted_times) if n > 0 else 0.0
        }

    def get_intent_accuracy(self) -> Dict[str, float]:
        """
        의도 분류 정확도 계산

        Returns:
            전체 정확도 및 의도별 정확도
        """
        if not self.intent_predictions:
            return {
                "overall": 0.0,
                "by_intent": {},
                "labeled_count": 0,
                "total_count": 0
            }

        # 실제 라벨이 있는 예측만 필터링
        labeled_predictions = [
            p for p in self.intent_predictions
            if p.get("actual") is not None
        ]

        if not labeled_predictions:
            return {
                "overall": 0.0,
                "by_intent": {},
                "labeled_count": 0,
                "total_count": len(self.intent_predictions)
            }

        # 전체 정확도
        correct = sum(
            1 for p in labeled_predictions
            if p["predicted"] == p["actual"]
        )
        overall_accuracy = correct / len(labeled_predictions)

        # 의도별 정확도
        by_intent = defaultdict(lambda: {"correct": 0, "total": 0})

        for p in labeled_predictions:
            actual = p["actual"]
            is_correct = p["predicted"] == actual

            by_intent[actual]["total"] += 1
            if is_correct:
                by_intent[actual]["correct"] += 1

        intent_accuracy = {
            intent: stats["correct"] / stats["total"]
            for intent, stats in by_intent.items()
        }

        return {
            "overall": overall_accuracy,
            "by_intent": intent_accuracy,
            "labeled_count": len(labeled_predictions),
            "total_count": len(self.intent_predictions)
        }

    def get_error_rate(self) -> float:
        """
        시스템 에러율 계산

        Returns:
            에러율 (0.0 ~ 1.0)
        """
        if self.total_requests == 0:
            return 0.0

        return self.error_count / self.total_requests

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        전체 성능 메트릭 요약

        Returns:
            성능 메트릭 딕셔너리
        """
        return {
            "response_times": self.get_response_time_percentiles(),
            "intent_accuracy": self.get_intent_accuracy(),
            "error_rate": self.get_error_rate(),
            "total_requests": self.total_requests,
            "error_count": self.error_count,
            "timestamp": datetime.now().isoformat()
        }

    def check_performance_thresholds(self) -> Dict[str, bool]:
        """
        성능 임계값 검증

        Returns:
            각 메트릭의 임계값 통과 여부
        """
        percentiles = self.get_response_time_percentiles()
        accuracy = self.get_intent_accuracy()
        error_rate = self.get_error_rate()

        return {
            "response_time_ok": percentiles["p95"] < 25.0,  # P95 < 25초
            "accuracy_ok": accuracy["overall"] >= 0.90,  # 정확도 >= 90%
            "error_rate_ok": error_rate < 0.01,  # 에러율 < 1%
            "all_ok": (
                percentiles["p95"] < 25.0 and
                (accuracy["overall"] >= 0.90 or accuracy["labeled_count"] == 0) and
                error_rate < 0.01
            )
        }

    def reset(self) -> None:
        """메트릭 리셋"""
        self._reset_metrics()
        logger.info("Performance metrics reset")


# 싱글톤 인스턴스
performance_monitor = PerformanceMonitor()
