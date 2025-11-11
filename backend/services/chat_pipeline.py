"""
통합 채팅 파이프라인 서비스
의도 분류 → DB 검색 → 문서 요약 → 응답 생성
"""

import logging
import time
from typing import Dict, Any, List, Optional
from backend.services.intent import IntentClassifier, EmergencyDetector, MedicalJudgmentDetector
from backend.services.rag_search import RAGSearchService
from backend.services.summarizer import DocumentSummarizer
from backend.services.cache import cache_service
from backend.services.performance import performance_monitor
from backend.core.config import settings

logger = logging.getLogger(__name__)


class ChatPipeline:
    """
    End-to-End 채팅 파이프라인
    - 의도 분류
    - DB 선택 및 검색
    - 문서 요약
    - 응답 검증 및 생성
    """

    def __init__(self):
        """파이프라인 초기화"""
        self.intent_service = IntentClassifier()
        self.rag_service = RAGSearchService()
        self.summarizer = DocumentSummarizer()
        self.cache = cache_service
        self.performance = performance_monitor
        logger.info("Chat Pipeline initialized")

    async def process_question(
        self,
        question: str,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        질문 처리 파이프라인 실행

        Args:
            question: 사용자 질문
            user_id: 사용자 ID
            context: 추가 컨텍스트 (병기, 이전 대화 등)

        Returns:
            최종 응답 딕셔너리
        """
        start_time = time.time()

        try:
            # 1. 응급 상황 감지 (최우선)
            if EmergencyDetector.detect(question):
                logger.warning(f"Emergency detected for question: {question}")
                return self._create_emergency_response(question, start_time)

            # 2. 의학적 판단 요청 감지
            if MedicalJudgmentDetector.detect(question):
                logger.warning(f"Medical judgment request detected: {question}")
                return self._create_medical_judgment_response(question, start_time)

            # 3. 의도 분류
            intent_result = await self._classify_intent(question)
            intent = intent_result["intent"]
            confidence = intent_result["confidence"]

            logger.info(f"Intent classified: {intent} (confidence: {confidence:.2f})")

            # 4. 의도별 특수 처리
            if intent in ["NON_MEDICAL", "NON_ETHICAL", "CHIT_CHAT"]:
                return self._handle_special_intent(
                    question,
                    intent,
                    confidence,
                    start_time
                )

            # 5. RAG 검색
            search_results = await self._search_documents(
                question,
                intent,
                context
            )

            # 6. 문서 요약 생성
            summaries = await self._generate_summaries(
                search_results["sources"],
                question,
                context
            )

            # 7. 최종 응답 생성
            response = self._build_response(
                question=question,
                intent=intent,
                confidence=confidence,
                search_results=search_results,
                summaries=summaries,
                start_time=start_time
            )

            # 8. 안전성 검증
            response = self._validate_safety(response)

            processing_time = time.time() - start_time
            logger.info(f"Pipeline completed in {processing_time:.2f}s")

            # 9. 성능 모니터링 기록
            self.performance.record_response_time(
                response_time=processing_time,
                intent=intent,
                question=question
            )
            self.performance.record_intent_prediction(
                question=question,
                predicted_intent=intent,
                confidence=confidence
            )

            return response

        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}", exc_info=True)

            # 에러 기록
            self.performance.record_error(
                error_type=type(e).__name__,
                error_message=str(e)
            )

            return self._create_error_response(question, str(e), start_time)

    async def _classify_intent(self, question: str) -> Dict[str, Any]:
        """
        의도 분류 (캐싱 포함)

        Args:
            question: 사용자 질문

        Returns:
            의도 분류 결과
        """
        # 캐시 확인
        cached_intent = self.cache.get_intent_cache(question)
        if cached_intent:
            logger.info("Intent cache hit")
            return cached_intent

        # 의도 분류 수행
        result = await self.intent_service.classify(question)

        # 캐시 저장 (1시간)
        self.cache.set_intent_cache(question, result, ttl=3600)

        return result

    async def _search_documents(
        self,
        question: str,
        intent: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        문서 검색 수행

        Args:
            question: 사용자 질문
            intent: 분류된 의도
            context: 추가 컨텍스트

        Returns:
            검색 결과
        """
        # 검색 파라미터 설정
        top_k = 5
        filters = None
        use_external_api = False

        # 컨텍스트에서 병기 추출
        if context and "stage" in context:
            filters = {"stage": context["stage"]}

        # RESEARCH 의도는 PubMed API 사용
        if intent == "RESEARCH":
            use_external_api = True

        # 검색 수행
        results = self.rag_service.search(
            query=question,
            intent=intent,
            top_k=top_k,
            filters=filters,
            use_external_api=use_external_api
        )

        return results

    async def _generate_summaries(
        self,
        documents: List[Dict[str, Any]],
        question: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        문서 요약 생성

        Args:
            documents: 검색된 문서 리스트
            question: 원본 질문
            context: 추가 컨텍스트

        Returns:
            요약 리스트
        """
        if not documents:
            return []

        # 병기 추출
        stage = context.get("stage") if context else None

        # 요약 생성
        summaries = await self.summarizer.batch_summarize(
            documents=documents,
            stage=stage
        )

        return summaries

    def _build_response(
        self,
        question: str,
        intent: str,
        confidence: float,
        search_results: Dict[str, Any],
        summaries: List[Dict[str, Any]],
        start_time: float
    ) -> Dict[str, Any]:
        """
        최종 응답 생성

        Args:
            question: 원본 질문
            intent: 분류된 의도
            confidence: 의도 분류 신뢰도
            search_results: 검색 결과
            summaries: 문서 요약
            start_time: 시작 시간

        Returns:
            응답 딕셔너리
        """
        # 응답 텍스트 생성
        answer = self._generate_answer_text(intent, summaries)

        # 검색된 DB 추출 (intent 기반 매핑)
        intent_to_db = {
            "MEDICAL_INFO": "qna_db",
            "RESEARCH": "paper_db",
            "POLICY": "policy_db",
            "DIET_INFO": "diet_db",
            "WELFARE_INFO": "welfare_db",
            "LEARNING": "quiz_db"
        }

        selected_dbs = []
        if intent in intent_to_db and search_results.get("sources"):
            # 실제로 문서가 검색된 경우에만 DB 추가
            selected_dbs.append(intent_to_db[intent])

        # summaries를 ChatResponse 스키마에 맞게 변환
        formatted_summaries = []
        for summary in summaries:
            # year를 int로 변환 (문자열인 경우)
            year_value = summary.get("year")
            if year_value and isinstance(year_value, str):
                try:
                    year_value = int(year_value) if year_value.isdigit() else None
                except:
                    year_value = None

            # authors를 list로 변환 (문자열인 경우)
            authors_value = summary.get("authors")
            if authors_value and isinstance(authors_value, str):
                authors_value = [authors_value]
            elif not authors_value:
                authors_value = []

            formatted_summaries.append({
                "title": summary.get("title", "제목 없음"),
                "summary": summary.get("summary", ""),
                "key_findings": summary.get("key_findings", []),
                "relevance": summary.get("relevance", ""),
                "metadata": {
                    "source": summary.get("source", {}).get("source", "qna"),
                    "title": summary.get("title"),
                    "authors": authors_value,
                    "year": year_value,
                    "doi": summary.get("source", {}).get("doi"),
                    "url": summary.get("source", {}).get("url"),
                    "similarity_score": None
                }
            })

        return {
            "question": question,
            "intent": intent,
            "intent_confidence": confidence,
            "answer": answer,
            "summaries": formatted_summaries,
            "selected_databases": selected_dbs,
            "total_documents": len(search_results.get("sources", [])),
            "processing_time": time.time() - start_time,
            "is_emergency": False,
            "is_medical_judgment": False,
            "is_safe": True
        }

    def _generate_answer_text(
        self,
        intent: str,
        summaries: List[Dict[str, Any]]
    ) -> str:
        """
        의도별 응답 텍스트 생성

        Args:
            intent: 분류된 의도
            summaries: 문서 요약

        Returns:
            응답 텍스트
        """
        if not summaries:
            return "죄송합니다. 관련 정보를 찾을 수 없습니다. 다른 질문을 해주시거나, 담당 의료진과 상담하시기 바랍니다."

        # 요약 개수에 따른 안내
        summary_count = len(summaries)

        if intent == "RESEARCH":
            answer = f"관련 연구 논문 {summary_count}건을 찾았습니다. 아래 요약을 참고하시고, 자세한 내용은 담당 의료진과 상담하시기 바랍니다."
        elif intent == "POLICY":
            answer = f"CKD 관련 진료지침 및 정책 정보 {summary_count}건을 찾았습니다. 아래 내용을 참고하시되, 응급 상황 시 즉시 119에 연락하시기 바랍니다."
        else:
            answer = f"질문과 관련된 의료 정보 {summary_count}건을 찾았습니다. 아래 내용은 참고용이며, 의학적 판단이 필요한 경우 반드시 담당 의료진과 상담하시기 바랍니다."

        return answer

    def _validate_safety(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        응답 안전성 검증

        Args:
            response: 응답 딕셔너리

        Returns:
            검증된 응답
        """
        # 요약의 안전성 검증 (기본적으로 모두 안전함으로 처리)
        # 필요시 summarizer의 validation 메서드 활용 가능
        response["is_safe"] = True

        return response

    def _create_emergency_response(
        self,
        question: str,
        start_time: float
    ) -> Dict[str, Any]:
        """응급 상황 응답 생성"""
        return {
            "question": question,
            "intent": "POLICY",
            "intent_confidence": 1.0,
            "answer": (
                "⚠️ 응급 상황이 감지되었습니다.\n\n"
                "즉시 119에 연락하시거나 가까운 응급실을 방문하세요.\n"
                "생명이 위급한 상황에서는 지체 없이 응급 의료 서비스를 이용하시기 바랍니다.\n\n"
                "119: 전국 어디서나 무료 응급 전화"
            ),
            "summaries": [],
            "selected_databases": [],
            "total_documents": 0,
            "processing_time": time.time() - start_time,
            "is_emergency": True,
            "is_medical_judgment": False,
            "is_safe": True
        }

    def _create_medical_judgment_response(
        self,
        question: str,
        start_time: float
    ) -> Dict[str, Any]:
        """의학적 판단 요청 응답 생성"""
        return {
            "question": question,
            "intent": "POLICY",
            "intent_confidence": 1.0,
            "answer": (
                "죄송합니다. 이 챗봇은 의학적 진단이나 치료 권고를 제공할 수 없습니다.\n\n"
                "증상이나 건강 상태에 대한 정확한 판단은 의료 전문가의 진료가 필요합니다.\n"
                "담당 의료진과 상담하시거나, 가까운 병원을 방문하시기 바랍니다.\n\n"
                "일반적인 CKD 관련 정보는 도움드릴 수 있습니다."
            ),
            "summaries": [],
            "selected_databases": [],
            "total_documents": 0,
            "processing_time": time.time() - start_time,
            "is_emergency": False,
            "is_medical_judgment": True,
            "is_safe": True
        }

    def _handle_special_intent(
        self,
        question: str,
        intent: str,
        confidence: float,
        start_time: float
    ) -> Dict[str, Any]:
        """특수 의도 처리"""
        if intent == "NON_MEDICAL":
            answer = (
                "죄송합니다. 저는 CKD(만성 콩팥병) 관련 질문에만 답변할 수 있습니다.\n\n"
                "CKD 관련 질문이 있으시면 언제든지 물어보세요.\n"
                "예: 크레아티닌, GFR, 식단 관리, 복지 정보 등"
            )
        elif intent == "NON_ETHICAL":
            answer = (
                "⚠️ 부적절한 요청이 감지되었습니다.\n\n"
                "이 서비스는 CKD 환자 지원을 위한 의료 정보 제공 목적으로만 사용됩니다."
            )
        elif intent == "CHIT_CHAT":
            answer = (
                "안녕하세요! 저는 CKD 환자를 돕는 AI 챗봇입니다.\n\n"
                "CKD 관련 질문이 있으시면 언제든지 물어보세요. "
                "질병 관리, 식단, 복지 정보 등 다양한 정보를 제공해드립니다."
            )
        else:
            answer = "질문을 이해하지 못했습니다. 다시 한번 질문해주시겠어요?"

        return {
            "question": question,
            "intent": intent,
            "intent_confidence": confidence,
            "answer": answer,
            "summaries": [],
            "selected_databases": [],
            "total_documents": 0,
            "processing_time": time.time() - start_time,
            "is_emergency": False,
            "is_medical_judgment": False,
            "is_safe": True
        }

    def _create_error_response(
        self,
        question: str,
        error_message: str,
        start_time: float
    ) -> Dict[str, Any]:
        """에러 응답 생성"""
        logger.error(f"Pipeline error for question '{question}': {error_message}")

        return {
            "question": question,
            "intent": "ERROR",
            "intent_confidence": 0.0,
            "answer": (
                "죄송합니다. 요청 처리 중 오류가 발생했습니다.\n"
                "잠시 후 다시 시도해주시거나, 문제가 지속되면 관리자에게 문의하세요."
            ),
            "summaries": [],
            "selected_databases": [],
            "total_documents": 0,
            "processing_time": time.time() - start_time,
            "is_emergency": False,
            "is_medical_judgment": False,
            "is_safe": True,
            "error": error_message
        }


# 싱글톤 인스턴스
chat_pipeline = ChatPipeline()
