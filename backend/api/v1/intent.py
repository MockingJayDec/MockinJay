"""
의도 분류 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, status
from backend.schemas.intent import (
    IntentClassifyRequest,
    IntentClassifyResponse,
    EmergencyResponse,
    MedicalReferralResponse
)
from backend.services.intent import intent_classifier, IntentType
from backend.core.logging import logger
import time

router = APIRouter(prefix="/intent", tags=["Intent Classification"])


@router.post("/classify", response_model=IntentClassifyResponse)
async def classify_intent(request: IntentClassifyRequest):
    """
    질문 의도 분류

    사용자 질문을 분석하여 의도를 분류합니다.
    - 응급 상황 자동 감지
    - 의학적 판단 요청 감지
    - 10개 의도 카테고리 분류
    """
    start_time = time.time()

    try:
        result = await intent_classifier.classify(request.question)

        # 응답 시간 체크
        elapsed = time.time() - start_time
        if elapsed > 2.0:
            logger.warning(f"Intent classification slow: {elapsed:.2f}s")

        logger.info(
            f"Intent classified: {result['intent']} "
            f"(confidence: {result['confidence']:.2f}, time: {elapsed:.2f}s)"
        )

        return IntentClassifyResponse(**result)

    except Exception as e:
        logger.error(f"Intent classification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="의도 분류 중 오류가 발생했습니다"
        )


@router.post("/check-emergency")
async def check_emergency(request: IntentClassifyRequest) -> dict:
    """
    응급 상황 감지

    질문에서 응급 키워드를 감지합니다.
    """
    try:
        result = await intent_classifier.classify(request.question)

        if result["is_emergency"]:
            return {
                "is_emergency": True,
                "response": EmergencyResponse(
                    message="⚠️ 응급 상황이 감지되었습니다. 즉시 119에 연락하세요!",
                    emergency_number="119",
                    actions=[
                        "즉시 119에 전화하세요",
                        "현재 위치와 증상을 명확히 설명하세요",
                        "안전한 장소에서 대기하세요",
                        "가능하면 주변 사람에게 도움을 요청하세요"
                    ]
                ).dict()
            }

        return {
            "is_emergency": False,
            "message": "응급 상황이 감지되지 않았습니다"
        }

    except Exception as e:
        logger.error(f"Emergency check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="응급 상황 감지 중 오류가 발생했습니다"
        )


@router.post("/check-medical-referral")
async def check_medical_referral(request: IntentClassifyRequest) -> dict:
    """
    의사 상담 필요 여부 확인

    의학적 판단이 필요한 질문인지 확인합니다.
    """
    try:
        result = await intent_classifier.classify(request.question)

        if result["needs_medical_referral"]:
            return {
                "needs_referral": True,
                "response": MedicalReferralResponse(
                    message="이 질문은 의료 전문가의 판단이 필요합니다.",
                    reason="증상 진단 및 치료는 의사만이 정확히 할 수 있습니다",
                    recommendations=[
                        "가까운 병원이나 의원을 방문하세요",
                        "증상, 검사 결과, 복용 중인 약물을 의사에게 알려주세요",
                        "자가 진단이나 자가 치료는 위험할 수 있습니다",
                        "정기적인 검진과 의사와의 상담이 중요합니다"
                    ]
                ).dict()
            }

        return {
            "needs_referral": False,
            "message": "일반적인 정보 제공이 가능한 질문입니다"
        }

    except Exception as e:
        logger.error(f"Medical referral check error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="의사 상담 필요 여부 확인 중 오류가 발생했습니다"
        )


@router.get("/intents")
async def get_intent_types():
    """
    지원하는 의도 타입 목록

    시스템이 분류할 수 있는 모든 의도 타입을 반환합니다.
    """
    return {
        "intents": [
            {
                "type": intent.value,
                "name": intent.name,
                "description": _get_intent_description(intent)
            }
            for intent in IntentType
        ]
    }


def _get_intent_description(intent: IntentType) -> str:
    """의도 타입 설명"""
    descriptions = {
        IntentType.MEDICAL_INFO: "CKD 관련 의료 정보 질의",
        IntentType.DIET_INFO: "식단, 영양 정보 질의",
        IntentType.RESEARCH: "의학 연구, 논문 검색",
        IntentType.WELFARE_INFO: "복지, 지원금 정보",
        IntentType.HEALTH_RECORD: "건강 기록 저장/조회",
        IntentType.LEARNING: "교육용 퀴즈, 학습",
        IntentType.POLICY: "진료지침, 응급상황",
        IntentType.CHIT_CHAT: "일상 대화, 인사",
        IntentType.NON_MEDICAL: "의료 외 질문",
        IntentType.NON_ETHICAL: "비윤리적 요청"
    }
    return descriptions.get(intent, "")
