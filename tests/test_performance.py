"""
성능 모니터링 서비스 테스트
"""
import pytest
from backend.services.performance import PerformanceMonitor


class TestPerformanceMonitor:
    """성능 모니터 테스트"""

    @pytest.fixture
    def monitor(self):
        """테스트용 모니터 인스턴스"""
        monitor = PerformanceMonitor()
        monitor.reset()  # 테스트 전 초기화
        return monitor

    def test_record_response_time(self, monitor):
        """응답 시간 기록 테스트"""
        monitor.record_response_time(
            response_time=2.5,
            intent="MEDICAL_INFO",
            question="크레아티닌이 뭔가요?"
        )

        assert len(monitor.response_times) == 1
        assert monitor.response_times[0] == 2.5
        assert monitor.total_requests == 1

    def test_response_time_percentiles(self, monitor):
        """응답 시간 백분위수 계산 테스트"""
        # 10개의 응답 시간 기록
        times = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        for t in times:
            monitor.record_response_time(t, "MEDICAL_INFO", "test")

        percentiles = monitor.get_response_time_percentiles()

        # 백분위수 계산: int(n * p) 인덱스 (0-based)
        # n=10: p50 = index 5 (6.0), p95 = index 9 (10.0), p99 = index 9 (10.0)
        assert percentiles["p50"] == 6.0  # 50 백분위수
        assert percentiles["p95"] == 10.0  # 95 백분위수
        assert percentiles["p99"] == 10.0  # 99 백분위수
        assert percentiles["mean"] == 5.5  # 평균
        assert percentiles["min"] == 1.0
        assert percentiles["max"] == 10.0

    def test_record_intent_prediction(self, monitor):
        """의도 분류 결과 기록 테스트"""
        monitor.record_intent_prediction(
            question="크레아티닌이 뭔가요?",
            predicted_intent="MEDICAL_INFO",
            confidence=0.95,
            actual_intent="MEDICAL_INFO"
        )

        assert len(monitor.intent_predictions) == 1
        prediction = monitor.intent_predictions[0]
        assert prediction["predicted"] == "MEDICAL_INFO"
        assert prediction["actual"] == "MEDICAL_INFO"
        assert prediction["confidence"] == 0.95

    def test_intent_accuracy_calculation(self, monitor):
        """의도 분류 정확도 계산 테스트"""
        # 정확한 예측 3개
        for _ in range(3):
            monitor.record_intent_prediction(
                question="test",
                predicted_intent="MEDICAL_INFO",
                confidence=0.95,
                actual_intent="MEDICAL_INFO"
            )

        # 틀린 예측 1개
        monitor.record_intent_prediction(
            question="test",
            predicted_intent="POLICY",
            confidence=0.80,
            actual_intent="MEDICAL_INFO"
        )

        accuracy = monitor.get_intent_accuracy()

        assert accuracy["overall"] == 0.75  # 3/4 = 75%
        assert accuracy["labeled_count"] == 4
        assert "MEDICAL_INFO" in accuracy["by_intent"]

    def test_record_error(self, monitor):
        """에러 기록 테스트"""
        monitor.record_error("ValueError", "Invalid input")

        assert monitor.error_count == 1
        assert monitor.total_requests == 1

    def test_error_rate_calculation(self, monitor):
        """에러율 계산 테스트"""
        # 성공 9개
        for _ in range(9):
            monitor.record_response_time(2.0, "MEDICAL_INFO", "test")

        # 실패 1개
        monitor.record_error("ValueError", "test error")

        error_rate = monitor.get_error_rate()

        assert error_rate == 0.1  # 1/10 = 10%

    def test_metrics_summary(self, monitor):
        """전체 메트릭 요약 테스트"""
        # 응답 시간 기록
        monitor.record_response_time(2.5, "MEDICAL_INFO", "test1")
        monitor.record_response_time(3.0, "POLICY", "test2")

        # 의도 분류 기록
        monitor.record_intent_prediction(
            "test", "MEDICAL_INFO", 0.95, "MEDICAL_INFO"
        )

        # 에러 기록
        monitor.record_error("ValueError", "test error")

        summary = monitor.get_metrics_summary()

        assert "response_times" in summary
        assert "intent_accuracy" in summary
        assert "error_rate" in summary
        assert summary["total_requests"] == 3
        assert summary["error_count"] == 1

    def test_performance_thresholds_all_pass(self, monitor):
        """성능 임계값 모두 통과 테스트"""
        # P95 < 25초
        for _ in range(20):
            monitor.record_response_time(10.0, "MEDICAL_INFO", "test")

        # 정확도 >= 90%
        for _ in range(10):
            monitor.record_intent_prediction(
                "test", "MEDICAL_INFO", 0.95, "MEDICAL_INFO"
            )

        # 에러율 < 1%
        # (이미 20개 성공, 에러 없음)

        thresholds = monitor.check_performance_thresholds()

        assert thresholds["response_time_ok"] is True
        assert thresholds["accuracy_ok"] is True
        assert thresholds["error_rate_ok"] is True
        assert thresholds["all_ok"] is True

    def test_performance_thresholds_response_time_fail(self, monitor):
        """응답 시간 임계값 실패 테스트"""
        # P95 > 25초
        for _ in range(20):
            monitor.record_response_time(30.0, "MEDICAL_INFO", "test")

        thresholds = monitor.check_performance_thresholds()

        assert thresholds["response_time_ok"] is False
        assert thresholds["all_ok"] is False

    def test_performance_thresholds_accuracy_fail(self, monitor):
        """정확도 임계값 실패 테스트"""
        # 정확도 < 90%
        # 8개 맞음
        for _ in range(8):
            monitor.record_intent_prediction(
                "test", "MEDICAL_INFO", 0.95, "MEDICAL_INFO"
            )

        # 2개 틀림
        for _ in range(2):
            monitor.record_intent_prediction(
                "test", "POLICY", 0.80, "MEDICAL_INFO"
            )

        thresholds = monitor.check_performance_thresholds()

        assert thresholds["accuracy_ok"] is False
        assert thresholds["all_ok"] is False

    def test_performance_thresholds_error_rate_fail(self, monitor):
        """에러율 임계값 실패 테스트"""
        # 95개 성공
        for _ in range(95):
            monitor.record_response_time(10.0, "MEDICAL_INFO", "test")

        # 5개 실패 (에러율 5%)
        for _ in range(5):
            monitor.record_error("ValueError", "test error")

        thresholds = monitor.check_performance_thresholds()

        assert thresholds["error_rate_ok"] is False
        assert thresholds["all_ok"] is False

    def test_reset(self, monitor):
        """메트릭 리셋 테스트"""
        # 데이터 기록
        monitor.record_response_time(2.5, "MEDICAL_INFO", "test")
        monitor.record_intent_prediction("test", "MEDICAL_INFO", 0.95)
        monitor.record_error("ValueError", "test error")

        assert monitor.total_requests > 0

        # 리셋
        monitor.reset()

        assert len(monitor.response_times) == 0
        assert len(monitor.intent_predictions) == 0
        assert monitor.error_count == 0
        assert monitor.total_requests == 0
