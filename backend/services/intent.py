"""
질문 의도 분류 서비스
Few-shot prompting을 사용한 의도 예측
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from backend.services.llm import llm_service
from backend.core.logging import logger
import json
import re


class IntentType(str, Enum):
    """질문 의도 타입"""
    MEDICAL_INFO = "MEDICAL_INFO"  # 의료 정보 질의
    DIET_INFO = "DIET_INFO"  # 식단 정보 질의
    RESEARCH = "RESEARCH"  # 의학 연구 검색
    WELFARE_INFO = "WELFARE_INFO"  # 복지 정보 질의
    HEALTH_RECORD = "HEALTH_RECORD"  # 건강 기록 관리
    LEARNING = "LEARNING"  # 교육 콘텐츠
    POLICY = "POLICY"  # 정책/응급상황
    CHIT_CHAT = "CHIT_CHAT"  # 일상 대화
    NON_MEDICAL = "NON_MEDICAL"  # 비의료 질문
    NON_ETHICAL = "NON_ETHICAL"  # 비윤리적 요청


class EmergencyDetector:
    """응급 상황 감지"""

    EMERGENCY_KEYWORDS = [
        "숨이 안쉬어져", "숨을 못쉬", "호흡곤란", "호흡 곤란",
        "가슴 아파", "가슴통증", "심장이 아파",
        "의식 없어", "정신 잃", "쓰러졌",
        "경련", "발작", "심한 통증",
        "피를 토해", "피가 나와", "출혈",
        "119", "응급실", "구급차"
    ]

    @classmethod
    def detect(cls, question: str) -> bool:
        """응급 상황 키워드 감지"""
        question_lower = question.lower().replace(" ", "")
        for keyword in cls.EMERGENCY_KEYWORDS:
            if keyword.replace(" ", "") in question_lower:
                logger.warning(f"Emergency detected: {keyword} in question")
                return True
        return False


class MedicalJudgmentDetector:
    """의학적 판단 요청 감지"""

    JUDGMENT_KEYWORDS = [
        "이 증상 뭐", "증상이 뭐", "병명", "질병명",
        "진단", "이거 무슨 병", "병이 뭐",
        "치료방법", "치료법", "어떻게 치료",
        "약 먹어", "약 추천", "약 알려줘"
    ]

    @classmethod
    def detect(cls, question: str) -> bool:
        """의학적 판단 요청 감지"""
        question_lower = question.lower().replace(" ", "")
        for keyword in cls.JUDGMENT_KEYWORDS:
            if keyword.replace(" ", "") in question_lower:
                logger.warning(f"Medical judgment request detected: {keyword}")
                return True
        return False


class IntentClassifier:
    """의도 분류기"""

    def __init__(self):
        self.few_shot_examples = self._load_few_shot_examples()

    def _load_few_shot_examples(self) -> Dict[str, List[str]]:
        """Few-shot 예시 로드"""
        return {
            "MEDICAL_INFO": [
                "크레아티닌 수치가 1.5인데 괜찮나요?",
                "GFR이란 무엇인가요?",
                "CKD 3기는 어떤 단계인가요?"
            ],
            "RESEARCH": [
                "CKD 환자의 빈혈 치료에 대한 최신 연구가 있나요?",
                "만성 콩팥병과 심혈관 질환 관련 논문을 찾아줘",
                "투석 환자의 삶의 질 연구 결과가 궁금해요"
            ],
            "POLICY": [
                "숨이 안쉬어져요 어떻게 해야 하나요?",
                "가슴이 너무 아픈데 응급실 가야 하나요?",
                "CKD 환자 진료지침이 궁금해요"
            ]
        }

    def _build_system_prompt(self) -> str:
        """시스템 프롬프트 생성"""
        examples_text = []
        for intent, examples in self.few_shot_examples.items():
            examples_text.append(f"\n{intent}:")
            for ex in examples:
                examples_text.append(f"  - {ex}")

        return f"""당신은 CKD(만성 콩팥병) 환자를 위한 의료 챗봇의 의도 분류 시스템입니다.

사용자 질문을 다음 카테고리 중 하나로 분류하세요:

- MEDICAL_INFO: CKD 관련 의료 정보 질의
- DIET_INFO: 식단, 영양 정보 질의
- RESEARCH: 의학 연구, 논문 검색
- WELFARE_INFO: 복지, 지원금 정보
- HEALTH_RECORD: 건강 기록 저장/조회
- LEARNING: 교육용 퀴즈, 학습
- POLICY: 진료지침, 응급상황
- CHIT_CHAT: 일상 대화, 인사
- NON_MEDICAL: 의료 외 질문
- NON_ETHICAL: 비윤리적 요청

Few-shot 예시:
{''.join(examples_text)}

응답은 반드시 다음 JSON 형식으로만 제공하세요:
{{"intent": "INTENT_TYPE", "confidence": 0.95, "reason": "분류 이유"}}"""

    async def classify(self, question: str) -> Dict[str, Any]:
        """
        질문 의도 분류

        Args:
            question: 사용자 질문

        Returns:
            {
                "intent": IntentType,
                "confidence": float,
                "reason": str,
                "is_emergency": bool,
                "needs_medical_referral": bool
            }
        """
        # 1. 응급 상황 우선 감지
        is_emergency = EmergencyDetector.detect(question)
        if is_emergency:
            return {
                "intent": IntentType.POLICY,
                "confidence": 1.0,
                "reason": "응급 상황 키워드 감지",
                "is_emergency": True,
                "needs_medical_referral": True
            }

        # 2. 의학적 판단 요청 감지
        needs_medical_referral = MedicalJudgmentDetector.detect(question)

        # 3. LLM 의도 분류
        try:
            system_prompt = self._build_system_prompt()
            user_prompt = f"다음 질문의 의도를 분류하세요:\n\n질문: {question}"

            response = await llm_service.chat_completion(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # 일관성을 위해 낮은 온도
                max_tokens=200
            )

            # JSON 파싱
            result = self._parse_response(response)
            result["is_emergency"] = False
            result["needs_medical_referral"] = needs_medical_referral

            return result

        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            # Fallback: 기본 의도 반환
            return {
                "intent": IntentType.MEDICAL_INFO,
                "confidence": 0.5,
                "reason": "분류 실패, 기본값 사용",
                "is_emergency": False,
                "needs_medical_referral": needs_medical_referral
            }

    def _parse_response(self, response: str) -> Dict[str, Any]:
        """LLM 응답 파싱"""
        try:
            # JSON 추출
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())

                # 의도 검증
                intent = data.get("intent", "MEDICAL_INFO")
                if intent not in [e.value for e in IntentType]:
                    intent = "MEDICAL_INFO"

                return {
                    "intent": IntentType(intent),
                    "confidence": float(data.get("confidence", 0.5)),
                    "reason": data.get("reason", "")
                }
        except Exception as e:
            logger.error(f"Response parsing failed: {e}")

        # Fallback
        return {
            "intent": IntentType.MEDICAL_INFO,
            "confidence": 0.5,
            "reason": "파싱 실패"
        }


# 전역 의도 분류기 인스턴스
intent_classifier = IntentClassifier()
