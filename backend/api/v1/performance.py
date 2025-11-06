"""
성능 모니터링 API 엔드포인트
"""
from fastapi import APIRouter
from typing import Dict, Any
from backend.services.performance import performance_monitor

router = APIRouter(
    prefix="/performance",
    tags=["performance"]
)


@router.get("/metrics", response_model=Dict[str, Any])
async def get_performance_metrics():
    """
    성능 메트릭 조회

    Returns:
        - response_times: 응답 시간 백분위수 (P50, P95, P99)
        - intent_accuracy: 의도 분류 정확도
        - error_rate: 시스템 에러율
        - total_requests: 총 요청 수
        - error_count: 에러 수
    """
    return performance_monitor.get_metrics_summary()


@router.get("/thresholds", response_model=Dict[str, bool])
async def check_performance_thresholds():
    """
    성능 임계값 검증

    Returns:
        - response_time_ok: P95 < 25초 여부
        - accuracy_ok: 정확도 >= 90% 여부
        - error_rate_ok: 에러율 < 1% 여부
        - all_ok: 모든 임계값 통과 여부
    """
    return performance_monitor.check_performance_thresholds()


@router.post("/reset")
async def reset_performance_metrics():
    """
    성능 메트릭 초기화

    Returns:
        성공 메시지
    """
    performance_monitor.reset()
    return {"message": "Performance metrics reset successfully"}
