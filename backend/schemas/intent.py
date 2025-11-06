"""
의도 분류 API 스키마
"""
from pydantic import BaseModel, Field
from backend.services.intent import IntentType


class IntentClassifyRequest(BaseModel):
    """의도 분류 요청"""
    question: str = Field(..., min_length=1, max_length=1000, description="사용자 질문")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "크레아티닌 수치가 1.5인데 괜찮나요?"
            }
        }


class IntentClassifyResponse(BaseModel):
    """의도 분류 응답"""
    intent: IntentType = Field(..., description="분류된 의도")
    confidence: float = Field(..., ge=0.0, le=1.0, description="신뢰도 (0.0-1.0)")
    reason: str = Field(..., description="분류 이유")
    is_emergency: bool = Field(default=False, description="응급 상황 여부")
    needs_medical_referral: bool = Field(default=False, description="의사 상담 필요 여부")

    class Config:
        json_schema_extra = {
            "example": {
                "intent": "MEDICAL_INFO",
                "confidence": 0.95,
                "reason": "크레아티닌 수치에 대한 의료 정보 질의",
                "is_emergency": False,
                "needs_medical_referral": False
            }
        }


class EmergencyResponse(BaseModel):
    """응급 상황 응답"""
    message: str = Field(..., description="응급 안내 메시지")
    emergency_number: str = Field(default="119", description="응급 전화번호")
    actions: list[str] = Field(..., description="즉시 취해야 할 행동")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "응급 상황이 감지되었습니다. 즉시 119에 연락하세요.",
                "emergency_number": "119",
                "actions": [
                    "즉시 119에 전화하세요",
                    "안전한 장소에서 대기하세요",
                    "주변 사람에게 도움을 요청하세요"
                ]
            }
        }


class MedicalReferralResponse(BaseModel):
    """의사 상담 권고 응답"""
    message: str = Field(..., description="상담 권고 메시지")
    reason: str = Field(..., description="권고 이유")
    recommendations: list[str] = Field(..., description="권장 사항")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "이 질문은 의료 전문가의 판단이 필요합니다.",
                "reason": "증상 진단은 의사만이 정확히 할 수 있습니다",
                "recommendations": [
                    "가까운 병원을 방문하세요",
                    "증상과 검사 결과를 의사에게 상담하세요",
                    "자가 진단은 위험할 수 있습니다"
                ]
            }
        }
