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


@router.get(
    "/metrics",
    response_model=Dict[str, Any],
    summary="성능 메트릭 조회",
    description="""
    현재 시스템의 성능 메트릭을 조회합니다.

    **반환 데이터**:
    - `response_times`: 응답 시간 백분위수
      - `p50`: 50 백분위수 (중앙값)
      - `p95`: 95 백분위수 (목표: < 25초)
      - `p99`: 99 백분위수
      - `mean`: 평균 응답 시간
      - `min`: 최소 응답 시간
      - `max`: 최대 응답 시간
    - `intent_accuracy`: 의도 분류 정확도
      - `overall`: 전체 정확도 (목표: >= 90%)
      - `by_intent`: 의도별 정확도
      - `labeled_count`: 라벨링된 예측 수
      - `total_count`: 총 예측 수
    - `error_rate`: 시스템 에러율 (목표: < 1%)
    - `total_requests`: 총 요청 수
    - `error_count`: 에러 발생 수
    - `timestamp`: 메트릭 수집 시각

    **사용 사례**:
    - 시스템 모니터링 대시보드
    - 성능 저하 탐지
    - SLA 준수 검증
    """
)
async def get_performance_metrics():
    """성능 메트릭 조회"""
    return performance_monitor.get_metrics_summary()


@router.get(
    "/thresholds",
    response_model=Dict[str, bool],
    summary="성능 임계값 검증",
    description="""
    시스템 성능이 정의된 임계값을 만족하는지 검증합니다.

    **임계값 기준**:
    - `response_time_ok`: P95 응답 시간 < 25초
    - `accuracy_ok`: 의도 분류 정확도 >= 90%
    - `error_rate_ok`: 시스템 에러율 < 1%
    - `all_ok`: 모든 임계값 통과 여부

    **반환값**: 각 임계값의 통과 여부 (boolean)

    **사용 사례**:
    - 알림 트리거 (임계값 미달 시)
    - CI/CD 파이프라인 검증
    - 배포 전 성능 체크
    """
)
async def check_performance_thresholds():
    """성능 임계값 검증"""
    return performance_monitor.check_performance_thresholds()


@router.post(
    "/reset",
    summary="성능 메트릭 초기화",
    description="""
    수집된 모든 성능 메트릭을 초기화합니다.

    **초기화 대상**:
    - 응답 시간 기록
    - 의도 분류 예측 기록
    - 에러 카운트
    - 총 요청 수

    **주의**: Redis에 캐시된 데이터는 유지됩니다 (7일간).

    **사용 사례**:
    - 테스트 후 메트릭 초기화
    - 새로운 성능 측정 시작
    - 배포 후 메트릭 리셋
    """
)
async def reset_performance_metrics():
    """성능 메트릭 초기화"""
    performance_monitor.reset()
    return {"message": "Performance metrics reset successfully"}
