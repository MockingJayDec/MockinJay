"""
채팅 API 엔드포인트 테스트
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from backend.main import app


client = TestClient(app)


class TestChatAPI:
    """채팅 API 테스트"""

    def test_chat_endpoint_success(self):
        """정상적인 채팅 요청 테스트"""
        request_data = {
            "question": "크레아티닌이 뭔가요?",
            "user_id": "test_user_001",
            "context": {"stage": "3"}
        }

        # Mock 파이프라인 응답
        mock_response = {
            "question": "크레아티닌이 뭔가요?",
            "intent": "MEDICAL_INFO",
            "intent_confidence": 0.95,
            "answer": "관련 의료 정보를 찾았습니다.",
            "summaries": [
                {
                    "title": "크레아티닌이란",
                    "summary": "신장 기능 지표",
                    "key_findings": ["신장 기능 평가"],
                    "relevance": "CKD 진단에 중요",
                    "metadata": {
                        "source": "qna",
                        "title": "크레아티닌이란"
                    }
                }
            ],
            "selected_databases": ["qna_db"],
            "total_documents": 1,
            "processing_time": 2.5,
            "is_emergency": False,
            "is_medical_judgment": False,
            "is_safe": True
        }

        with patch(
            'backend.services.chat_pipeline.chat_pipeline.process_question',
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            response = client.post("/api/v1/chat", json=request_data)

            assert response.status_code == 200
            data = response.json()

            assert data["question"] == "크레아티닌이 뭔가요?"
            assert data["intent"] == "MEDICAL_INFO"
            assert data["intent_confidence"] == 0.95
            assert len(data["summaries"]) > 0
            assert data["is_emergency"] is False
            assert data["is_safe"] is True

    def test_chat_endpoint_emergency(self):
        """응급 상황 테스트"""
        request_data = {
            "question": "숨이 안쉬어져요 도와주세요"
        }

        mock_response = {
            "question": "숨이 안쉬어져요 도와주세요",
            "intent": "POLICY",
            "intent_confidence": 1.0,
            "answer": "⚠️ 응급 상황이 감지되었습니다. 즉시 119에 연락하세요.",
            "summaries": [],
            "selected_databases": [],
            "total_documents": 0,
            "processing_time": 0.1,
            "is_emergency": True,
            "is_medical_judgment": False,
            "is_safe": True
        }

        with patch(
            'backend.services.chat_pipeline.chat_pipeline.process_question',
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            response = client.post("/api/v1/chat", json=request_data)

            assert response.status_code == 200
            data = response.json()

            assert data["is_emergency"] is True
            assert "119" in data["answer"]
            assert data["intent"] == "POLICY"

    def test_chat_endpoint_medical_judgment(self):
        """의학적 판단 요청 테스트"""
        request_data = {
            "question": "이 증상이 무슨 병인가요?"
        }

        mock_response = {
            "question": "이 증상이 무슨 병인가요?",
            "intent": "POLICY",
            "intent_confidence": 1.0,
            "answer": "의학적 진단이나 치료 권고를 제공할 수 없습니다.",
            "summaries": [],
            "selected_databases": [],
            "total_documents": 0,
            "processing_time": 0.1,
            "is_emergency": False,
            "is_medical_judgment": True,
            "is_safe": True
        }

        with patch(
            'backend.services.chat_pipeline.chat_pipeline.process_question',
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            response = client.post("/api/v1/chat", json=request_data)

            assert response.status_code == 200
            data = response.json()

            assert data["is_medical_judgment"] is True
            assert "의학적 진단" in data["answer"] or "의료 전문가" in data["answer"]

    def test_chat_endpoint_validation_error(self):
        """잘못된 요청 검증 테스트"""
        # 빈 질문
        request_data = {
            "question": ""
        }

        response = client.post("/api/v1/chat", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_timeout(self):
        """타임아웃 테스트"""
        request_data = {
            "question": "크레아티닌이 뭔가요?"
        }

        # Timeout 시뮬레이션
        import asyncio
        async def timeout_error(*args, **kwargs):
            raise asyncio.TimeoutError()

        with patch(
            'backend.services.chat_pipeline.chat_pipeline.process_question',
            new_callable=AsyncMock,
            side_effect=timeout_error
        ):
            response = client.post("/api/v1/chat", json=request_data)

            assert response.status_code == 504  # Gateway Timeout
            assert "초과" in response.json()["detail"]

    def test_chat_endpoint_server_error(self):
        """서버 에러 테스트"""
        request_data = {
            "question": "크레아티닌이 뭔가요?"
        }

        # 서버 에러 시뮬레이션
        with patch(
            'backend.services.chat_pipeline.chat_pipeline.process_question',
            new_callable=AsyncMock,
            side_effect=Exception("Internal error")
        ):
            response = client.post("/api/v1/chat", json=request_data)

            assert response.status_code == 500
            assert "오류" in response.json()["detail"]

    def test_chat_health_endpoint(self):
        """헬스 체크 엔드포인트 테스트"""
        mock_response = {
            "question": "안녕하세요",
            "intent": "CHIT_CHAT",
            "processing_time": 0.5,
            "answer": "안녕하세요!",
            "summaries": [],
            "selected_databases": [],
            "total_documents": 0,
            "is_emergency": False,
            "is_medical_judgment": False,
            "is_safe": True,
            "intent_confidence": 0.98
        }

        with patch(
            'backend.services.chat_pipeline.chat_pipeline.process_question',
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            response = client.get("/api/v1/chat/health")

            assert response.status_code == 200
            data = response.json()

            assert data["status"] == "healthy"
            assert data["pipeline"] == "operational"
            assert "test_response_time" in data

    def test_chat_endpoint_without_user_id(self):
        """user_id 없이 요청 테스트"""
        request_data = {
            "question": "크레아티닌이 뭔가요?"
        }

        mock_response = {
            "question": "크레아티닌이 뭔가요?",
            "intent": "MEDICAL_INFO",
            "intent_confidence": 0.95,
            "answer": "관련 정보를 찾았습니다.",
            "summaries": [],
            "selected_databases": [],
            "total_documents": 0,
            "processing_time": 1.0,
            "is_emergency": False,
            "is_medical_judgment": False,
            "is_safe": True
        }

        with patch(
            'backend.services.chat_pipeline.chat_pipeline.process_question',
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            response = client.post("/api/v1/chat", json=request_data)

            assert response.status_code == 200
            # user_id는 선택사항이므로 성공해야 함

    def test_chat_endpoint_with_context(self):
        """컨텍스트와 함께 요청 테스트"""
        request_data = {
            "question": "크레아티닌이 뭔가요?",
            "context": {
                "stage": "3",
                "previous_questions": ["GFR이 뭔가요?"]
            }
        }

        mock_response = {
            "question": "크레아티닌이 뭔가요?",
            "intent": "MEDICAL_INFO",
            "intent_confidence": 0.95,
            "answer": "3기 환자를 위한 정보입니다.",
            "summaries": [],
            "selected_databases": [],
            "total_documents": 0,
            "processing_time": 1.5,
            "is_emergency": False,
            "is_medical_judgment": False,
            "is_safe": True
        }

        with patch(
            'backend.services.chat_pipeline.chat_pipeline.process_question',
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            response = client.post("/api/v1/chat", json=request_data)

            assert response.status_code == 200
            data = response.json()

            # 컨텍스트가 올바르게 처리되었는지 확인
            assert data["question"] == "크레아티닌이 뭔가요?"

    def test_chat_endpoint_long_question(self):
        """긴 질문 테스트"""
        request_data = {
            "question": "a" * 1001  # 1000자 제한 초과
        }

        response = client.post("/api/v1/chat", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_chat_endpoint_research_intent(self):
        """연구 논문 검색 의도 테스트"""
        request_data = {
            "question": "CKD 빈혈 치료 최신 연구"
        }

        mock_response = {
            "question": "CKD 빈혈 치료 최신 연구",
            "intent": "RESEARCH",
            "intent_confidence": 0.92,
            "answer": "관련 연구 논문 3건을 찾았습니다.",
            "summaries": [
                {
                    "title": "Anemia in CKD",
                    "summary": "빈혈 치료 연구",
                    "key_findings": ["효과적", "부작용 적음"],
                    "relevance": "최신 지침",
                    "metadata": {
                        "source": "pubmed",
                        "title": "Anemia in CKD",
                        "year": 2023
                    }
                }
            ],
            "selected_databases": ["paper_db"],
            "total_documents": 3,
            "processing_time": 5.2,
            "is_emergency": False,
            "is_medical_judgment": False,
            "is_safe": True
        }

        with patch(
            'backend.services.chat_pipeline.chat_pipeline.process_question',
            new_callable=AsyncMock,
            return_value=mock_response
        ):
            response = client.post("/api/v1/chat", json=request_data)

            assert response.status_code == 200
            data = response.json()

            assert data["intent"] == "RESEARCH"
            assert "paper_db" in data["selected_databases"]
            assert len(data["summaries"]) > 0
