"""
의도 분류 시스템 테스트
"""
import pytest
from backend.services.intent import (
    IntentClassifier,
    EmergencyDetector,
    MedicalJudgmentDetector,
    IntentType
)


class TestEmergencyDetector:
    """응급 상황 감지 테스트"""

    def test_detect_emergency_keywords(self):
        """응급 키워드 감지"""
        test_cases = [
            ("숨이 안쉬어져요", True),
            ("가슴이 너무 아파요", True),
            ("의식을 잃었어요", True),
            ("호흡곤란이 있어요", True),
            ("119 불러주세요", True),
            ("크레아티닌 수치가 궁금해요", False),
            ("식단 추천 부탁드려요", False)
        ]

        for question, expected in test_cases:
            result = EmergencyDetector.detect(question)
            assert result == expected, f"Failed for: {question}"

    def test_case_insensitive_detection(self):
        """대소문자 구분 없이 감지"""
        assert EmergencyDetector.detect("숨이 안쉬어져요") == True
        assert EmergencyDetector.detect("EMERGENCY") == False

    def test_whitespace_handling(self):
        """공백 처리"""
        assert EmergencyDetector.detect("호 흡 곤 란") == True
        assert EmergencyDetector.detect("호흡곤란") == True


class TestMedicalJudgmentDetector:
    """의학적 판단 요청 감지 테스트"""

    def test_detect_judgment_requests(self):
        """의학적 판단 요청 감지"""
        test_cases = [
            ("이 증상 뭐에요?", True),
            ("진단해주세요", True),
            ("무슨 병인가요?", True),
            ("약 추천해주세요", True),
            ("크레아티닌이 뭐에요?", False),
            ("CKD 관리 방법 알려주세요", False)
        ]

        for question, expected in test_cases:
            result = MedicalJudgmentDetector.detect(question)
            assert result == expected, f"Failed for: {question}"


class TestIntentClassifier:
    """의도 분류기 테스트"""

    @pytest.fixture
    def classifier(self):
        """분류기 인스턴스"""
        return IntentClassifier()

    def test_few_shot_examples_loaded(self, classifier):
        """Few-shot 예시 로드 확인"""
        assert len(classifier.few_shot_examples) > 0
        assert "MEDICAL_INFO" in classifier.few_shot_examples
        assert "RESEARCH" in classifier.few_shot_examples
        assert "POLICY" in classifier.few_shot_examples

    def test_system_prompt_generation(self, classifier):
        """시스템 프롬프트 생성"""
        prompt = classifier._build_system_prompt()
        assert "CKD" in prompt
        assert "MEDICAL_INFO" in prompt
        assert "RESEARCH" in prompt
        assert "JSON" in prompt

    @pytest.mark.asyncio
    async def test_emergency_classification(self, classifier):
        """응급 상황 분류"""
        result = await classifier.classify("숨이 안쉬어져요 도와주세요")
        assert result["intent"] == IntentType.POLICY
        assert result["is_emergency"] == True
        assert result["confidence"] == 1.0

    @pytest.mark.asyncio
    async def test_medical_referral_classification(self, classifier):
        """의학적 판단 요청 분류"""
        result = await classifier.classify("이 증상 뭐에요?")
        assert result["needs_medical_referral"] == True

    def test_response_parsing(self, classifier):
        """응답 파싱 테스트"""
        # 정상 JSON
        response = '{"intent": "MEDICAL_INFO", "confidence": 0.95, "reason": "test"}'
        result = classifier._parse_response(response)
        assert result["intent"] == IntentType.MEDICAL_INFO
        assert result["confidence"] == 0.95

        # 잘못된 JSON (fallback)
        response = "Invalid JSON"
        result = classifier._parse_response(response)
        assert result["intent"] == IntentType.MEDICAL_INFO
        assert result["confidence"] == 0.5


@pytest.mark.asyncio
async def test_intent_api_endpoint():
    """API 엔드포인트 통합 테스트"""
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)

    # 정상 요청
    response = client.post(
        "/api/v1/intent/classify",
        json={"question": "크레아티닌 수치가 궁금해요"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "intent" in data
    assert "confidence" in data
    assert "reason" in data

    # 빈 질문 (validation error)
    response = client.post(
        "/api/v1/intent/classify",
        json={"question": ""}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_emergency_endpoint():
    """응급 감지 엔드포인트 테스트"""
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)

    # 응급 상황
    response = client.post(
        "/api/v1/intent/check-emergency",
        json={"question": "숨이 안쉬어져요"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_emergency"] == True
    assert "119" in data["response"]["emergency_number"]

    # 비응급
    response = client.post(
        "/api/v1/intent/check-emergency",
        json={"question": "크레아티닌이 뭐에요?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_emergency"] == False


@pytest.mark.asyncio
async def test_medical_referral_endpoint():
    """의사 상담 권고 엔드포인트 테스트"""
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)

    # 의학적 판단 요청
    response = client.post(
        "/api/v1/intent/check-medical-referral",
        json={"question": "이 증상 뭐에요?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["needs_referral"] == True

    # 일반 질문
    response = client.post(
        "/api/v1/intent/check-medical-referral",
        json={"question": "CKD가 뭐에요?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["needs_referral"] == False


def test_get_intent_types():
    """의도 타입 목록 조회 테스트"""
    from fastapi.testclient import TestClient
    from backend.main import app

    client = TestClient(app)

    response = client.get("/api/v1/intent/intents")
    assert response.status_code == 200
    data = response.json()
    assert "intents" in data
    assert len(data["intents"]) == 10  # 10개 의도 타입
