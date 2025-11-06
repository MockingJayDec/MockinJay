"""
성능 모니터링 API 엔드포인트 테스트
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.main import app
from backend.services.performance import performance_monitor


client = TestClient(app)


class TestPerformanceAPI:
    """성능 API 테스트"""

    @pytest.fixture(autouse=True)
    def reset_monitor(self):
        """각 테스트 전후 모니터 리셋"""
        performance_monitor.reset()
        yield
        performance_monitor.reset()

    def test_get_metrics_endpoint(self):
        """메트릭 조회 엔드포인트 테스트"""
        # 일부 데이터 기록
        performance_monitor.record_response_time(2.5, "MEDICAL_INFO", "test")
        performance_monitor.record_intent_prediction(
            "test", "MEDICAL_INFO", 0.95, "MEDICAL_INFO"
        )

        response = client.get("/api/v1/performance/metrics")

        assert response.status_code == 200
        data = response.json()

        assert "response_times" in data
        assert "intent_accuracy" in data
        assert "error_rate" in data
        assert "total_requests" in data
        assert data["total_requests"] == 1

    def test_get_metrics_empty(self):
        """빈 메트릭 조회 테스트"""
        response = client.get("/api/v1/performance/metrics")

        assert response.status_code == 200
        data = response.json()

        assert data["total_requests"] == 0
        assert data["error_count"] == 0
        assert data["error_rate"] == 0.0

    def test_check_thresholds_endpoint(self):
        """임계값 검증 엔드포인트 테스트"""
        # 성공 데이터 기록
        for _ in range(10):
            performance_monitor.record_response_time(10.0, "MEDICAL_INFO", "test")

        for _ in range(10):
            performance_monitor.record_intent_prediction(
                "test", "MEDICAL_INFO", 0.95, "MEDICAL_INFO"
            )

        response = client.get("/api/v1/performance/thresholds")

        assert response.status_code == 200
        data = response.json()

        assert "response_time_ok" in data
        assert "accuracy_ok" in data
        assert "error_rate_ok" in data
        assert "all_ok" in data
        assert data["all_ok"] is True

    def test_check_thresholds_fail(self):
        """임계값 검증 실패 테스트"""
        # P95 > 25초 데이터 기록
        for _ in range(20):
            performance_monitor.record_response_time(30.0, "MEDICAL_INFO", "test")

        response = client.get("/api/v1/performance/thresholds")

        assert response.status_code == 200
        data = response.json()

        assert data["response_time_ok"] is False
        assert data["all_ok"] is False

    def test_reset_endpoint(self):
        """메트릭 리셋 엔드포인트 테스트"""
        # 데이터 기록
        performance_monitor.record_response_time(2.5, "MEDICAL_INFO", "test")
        performance_monitor.record_error("ValueError", "test error")

        assert performance_monitor.total_requests > 0

        # 리셋 요청
        response = client.post("/api/v1/performance/reset")

        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert "reset" in data["message"].lower()

        # 메트릭 확인
        metrics_response = client.get("/api/v1/performance/metrics")
        metrics_data = metrics_response.json()

        assert metrics_data["total_requests"] == 0
        assert metrics_data["error_count"] == 0

    def test_integration_with_chat(self):
        """채팅 API와 통합 테스트"""
        from unittest.mock import AsyncMock

        async def mock_process_question(*args, **kwargs):
            """Mock 함수가 실제로 성능 모니터링을 호출"""
            # 실제 성능 모니터링 기록
            performance_monitor.record_response_time(
                response_time=2.5,
                intent="MEDICAL_INFO",
                question="test"
            )
            performance_monitor.record_intent_prediction(
                question="test",
                predicted_intent="MEDICAL_INFO",
                confidence=0.95
            )

            return {
                "question": "test",
                "intent": "MEDICAL_INFO",
                "intent_confidence": 0.95,
                "answer": "test answer",
                "summaries": [],
                "selected_databases": [],
                "total_documents": 0,
                "processing_time": 2.5,
                "is_emergency": False,
                "is_medical_judgment": False,
                "is_safe": True
            }

        with patch(
            'backend.services.chat_pipeline.chat_pipeline.process_question',
            side_effect=mock_process_question
        ):
            # 채팅 요청
            chat_response = client.post(
                "/api/v1/chat",
                json={"question": "test"}
            )

            assert chat_response.status_code == 200

            # 성능 메트릭 확인
            metrics_response = client.get("/api/v1/performance/metrics")
            metrics_data = metrics_response.json()

            assert metrics_data["total_requests"] == 1
            assert len(performance_monitor.response_times) == 1

    def test_metrics_with_multiple_requests(self):
        """여러 요청에 대한 메트릭 테스트"""
        # 다양한 응답 시간 기록
        times = [1.5, 2.0, 2.5, 3.0, 10.0, 15.0, 20.0, 22.0, 23.0, 24.0]

        for t in times:
            performance_monitor.record_response_time(t, "MEDICAL_INFO", "test")

        response = client.get("/api/v1/performance/metrics")

        assert response.status_code == 200
        data = response.json()

        response_times = data["response_times"]
        assert response_times["p95"] < 25.0  # 임계값 통과
        assert data["total_requests"] == 10

    def test_error_tracking_in_metrics(self):
        """에러 추적 메트릭 테스트"""
        # 90개 성공
        for _ in range(90):
            performance_monitor.record_response_time(2.0, "MEDICAL_INFO", "test")

        # 10개 실패
        for _ in range(10):
            performance_monitor.record_error("ValueError", "test error")

        response = client.get("/api/v1/performance/metrics")

        assert response.status_code == 200
        data = response.json()

        assert data["total_requests"] == 100
        assert data["error_count"] == 10
        assert data["error_rate"] == 0.1  # 10%

        # 임계값 검증
        thresholds_response = client.get("/api/v1/performance/thresholds")
        thresholds_data = thresholds_response.json()

        assert thresholds_data["error_rate_ok"] is False  # 1% 초과
