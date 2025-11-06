"""
통합 채팅 파이프라인 테스트
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from backend.services.chat_pipeline import ChatPipeline


class TestChatPipeline:
    """채팅 파이프라인 테스트"""

    @pytest.fixture
    def pipeline(self):
        """파이프라인 인스턴스"""
        return ChatPipeline()

    @pytest.mark.asyncio
    async def test_emergency_detection(self, pipeline):
        """응급 상황 감지 테스트"""
        question = "숨이 안쉬어져요 도와주세요"

        result = await pipeline.process_question(question)

        assert result["is_emergency"] is True
        assert result["intent"] == "POLICY"
        assert "119" in result["answer"]
        assert "응급" in result["answer"]

    @pytest.mark.asyncio
    async def test_medical_judgment_detection(self, pipeline):
        """의학적 판단 요청 감지 테스트"""
        question = "이 증상이 무슨 병인가요?"

        result = await pipeline.process_question(question)

        assert result["is_medical_judgment"] is True
        assert result["intent"] == "POLICY"
        assert "의학적 진단" in result["answer"] or "의료 전문가" in result["answer"]

    @pytest.mark.asyncio
    async def test_non_medical_intent(self, pipeline):
        """비의료 질문 처리 테스트"""
        question = "오늘 날씨 어때?"

        with patch.object(
            pipeline.intent_service,
            'classify_intent',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.return_value = {
                "intent": "NON_MEDICAL",
                "confidence": 0.95,
                "reason": "비의료 질문"
            }

            result = await pipeline.process_question(question)

            assert result["intent"] == "NON_MEDICAL"
            assert "CKD" in result["answer"]
            assert len(result["summaries"]) == 0

    @pytest.mark.asyncio
    async def test_chit_chat_intent(self, pipeline):
        """일상 대화 처리 테스트"""
        question = "안녕하세요"

        with patch.object(
            pipeline.intent_service,
            'classify_intent',
            new_callable=AsyncMock
        ) as mock_classify:
            mock_classify.return_value = {
                "intent": "CHIT_CHAT",
                "confidence": 0.98,
                "reason": "인사"
            }

            result = await pipeline.process_question(question)

            assert result["intent"] == "CHIT_CHAT"
            assert "챗봇" in result["answer"] or "AI" in result["answer"]

    @pytest.mark.asyncio
    async def test_medical_info_pipeline(self, pipeline):
        """의료 정보 질의 파이프라인 테스트"""
        question = "크레아티닌이 뭔가요?"

        # Mock 의도 분류
        with patch.object(
            pipeline.intent_service,
            'classify_intent',
            new_callable=AsyncMock
        ) as mock_intent:
            mock_intent.return_value = {
                "intent": "MEDICAL_INFO",
                "confidence": 0.95,
                "reason": "의료 정보 질의"
            }

            # Mock RAG 검색
            with patch.object(
                pipeline.rag_service,
                'search'
            ) as mock_search:
                mock_search.return_value = {
                    "query": question,
                    "intent": "MEDICAL_INFO",
                    "sources": [
                        {
                            "document": "크레아티닌은 신장 기능 지표입니다.",
                            "metadata": {
                                "collection": "qna_db",
                                "source": "qna"
                            }
                        }
                    ],
                    "search_metadata": {
                        "total_results": 1
                    }
                }

                # Mock 요약 생성
                with patch.object(
                    pipeline.summarizer,
                    'summarize_documents'
                ) as mock_summarize:
                    mock_summarize.return_value = {
                        "summaries": [
                            {
                                "title": "크레아티닌이란",
                                "summary": "신장 기능을 평가하는 혈액 검사 지표",
                                "key_findings": ["신장 기능 평가", "혈액 검사"],
                                "relevance": "CKD 진단에 중요한 지표"
                            }
                        ]
                    }

                    result = await pipeline.process_question(question)

                    assert result["intent"] == "MEDICAL_INFO"
                    assert result["intent_confidence"] == 0.95
                    assert len(result["summaries"]) > 0
                    assert result["total_documents"] > 0
                    assert result["is_emergency"] is False
                    assert result["is_safe"] is True

    @pytest.mark.asyncio
    async def test_research_intent_pipeline(self, pipeline):
        """연구 논문 검색 파이프라인 테스트"""
        question = "CKD 빈혈 치료 최신 연구"

        with patch.object(
            pipeline.intent_service,
            'classify_intent',
            new_callable=AsyncMock
        ) as mock_intent:
            mock_intent.return_value = {
                "intent": "RESEARCH",
                "confidence": 0.92,
                "reason": "연구 논문 검색"
            }

            with patch.object(
                pipeline.rag_service,
                'search'
            ) as mock_search:
                mock_search.return_value = {
                    "query": question,
                    "intent": "RESEARCH",
                    "sources": [
                        {
                            "document": "CKD 환자의 빈혈 치료 연구 초록",
                            "metadata": {
                                "collection": "paper_db",
                                "source": "pubmed",
                                "title": "Anemia in CKD",
                                "authors": ["Smith et al."],
                                "year": 2023
                            }
                        }
                    ],
                    "search_metadata": {
                        "total_results": 1,
                        "external_api_used": True
                    }
                }

                with patch.object(
                    pipeline.summarizer,
                    'summarize_documents'
                ) as mock_summarize:
                    mock_summarize.return_value = {
                        "summaries": [
                            {
                                "title": "Anemia in CKD",
                                "summary": "CKD 환자 빈혈 치료 방법 연구",
                                "key_findings": ["치료 효과", "부작용 평가"],
                                "relevance": "최신 치료 지침 제공"
                            }
                        ]
                    }

                    result = await pipeline.process_question(question)

                    assert result["intent"] == "RESEARCH"
                    assert "연구" in result["answer"] or "논문" in result["answer"]

    @pytest.mark.asyncio
    async def test_caching_intent(self, pipeline):
        """의도 분류 캐싱 테스트"""
        question = "크레아티닌이 뭔가요?"

        # 첫 번째 호출 - 캐시 미스
        with patch.object(
            pipeline.cache,
            'get_intent_cache',
            return_value=None
        ):
            with patch.object(
                pipeline.cache,
                'set_intent_cache',
                return_value=True
            ) as mock_set_cache:
                with patch.object(
                    pipeline.intent_service,
                    'classify_intent',
                    new_callable=AsyncMock
                ) as mock_classify:
                    mock_classify.return_value = {
                        "intent": "MEDICAL_INFO",
                        "confidence": 0.95,
                        "reason": "의료 정보"
                    }

                    await pipeline._classify_intent(question)

                    # 캐시 저장 확인
                    mock_set_cache.assert_called_once()

        # 두 번째 호출 - 캐시 히트
        cached_result = {
            "intent": "MEDICAL_INFO",
            "confidence": 0.95,
            "reason": "의료 정보"
        }

        with patch.object(
            pipeline.cache,
            'get_intent_cache',
            return_value=cached_result
        ):
            with patch.object(
                pipeline.intent_service,
                'classify_intent',
                new_callable=AsyncMock
            ) as mock_classify:
                result = await pipeline._classify_intent(question)

                # LLM 호출 없이 캐시에서 반환
                mock_classify.assert_not_called()
                assert result == cached_result

    @pytest.mark.asyncio
    async def test_timeout_handling(self, pipeline):
        """타임아웃 처리 테스트"""
        question = "크레아티닌이 뭔가요?"

        # 긴 처리 시간 시뮬레이션
        async def slow_classify(*args, **kwargs):
            await asyncio.sleep(25)  # 25초 대기
            return {"intent": "MEDICAL_INFO", "confidence": 0.9}

        with patch.object(
            pipeline,
            '_classify_intent',
            side_effect=slow_classify
        ):
            # 파이프라인 자체는 에러 응답 반환
            result = await pipeline.process_question(question)

            # 에러 응답 확인
            assert "error" in result or result["intent"] == "ERROR"

    @pytest.mark.asyncio
    async def test_error_handling(self, pipeline):
        """에러 처리 테스트"""
        question = "크레아티닌이 뭔가요?"

        # 의도 분류 에러 시뮬레이션
        with patch.object(
            pipeline.intent_service,
            'classify_intent',
            new_callable=AsyncMock,
            side_effect=Exception("LLM API 에러")
        ):
            result = await pipeline.process_question(question)

            # 에러 응답 생성 확인
            assert "error" in result or result["intent"] == "ERROR"
            assert "오류" in result["answer"]

    @pytest.mark.asyncio
    async def test_safety_validation(self, pipeline):
        """안전성 검증 테스트"""
        question = "크레아티닌이 뭔가요?"

        with patch.object(
            pipeline.intent_service,
            'classify_intent',
            new_callable=AsyncMock
        ) as mock_intent:
            mock_intent.return_value = {
                "intent": "MEDICAL_INFO",
                "confidence": 0.95,
                "reason": "의료 정보"
            }

            with patch.object(
                pipeline.rag_service,
                'search'
            ) as mock_search:
                mock_search.return_value = {
                    "sources": [{"document": "test"}],
                    "search_metadata": {"total_results": 1}
                }

                with patch.object(
                    pipeline.summarizer,
                    'summarize_documents'
                ) as mock_summarize:
                    mock_summarize.return_value = {
                        "summaries": [
                            {
                                "title": "Test",
                                "summary": "부적절한 내용 포함",
                                "key_findings": [],
                                "relevance": "관련성"
                            }
                        ]
                    }

                    # 안전하지 않은 요약 필터링
                    with patch.object(
                        pipeline.safety_validator,
                        'validate_summary',
                        return_value=False
                    ):
                        result = await pipeline.process_question(question)

                        # 필터링 후 응답 확인
                        assert result["is_safe"] is False
                        assert len(result["summaries"]) == 0

    @pytest.mark.asyncio
    async def test_processing_time_tracking(self, pipeline):
        """처리 시간 추적 테스트"""
        question = "크레아티닌이 뭔가요?"

        result = await pipeline.process_question(question)

        # 처리 시간 기록 확인
        assert "processing_time" in result
        assert result["processing_time"] >= 0
        assert result["processing_time"] < 30  # 30초 이내

    @pytest.mark.asyncio
    async def test_context_handling(self, pipeline):
        """컨텍스트 처리 테스트"""
        question = "크레아티닌이 뭔가요?"
        context = {"stage": "3"}

        with patch.object(
            pipeline.intent_service,
            'classify_intent',
            new_callable=AsyncMock
        ) as mock_intent:
            mock_intent.return_value = {
                "intent": "MEDICAL_INFO",
                "confidence": 0.95,
                "reason": "의료 정보"
            }

            with patch.object(
                pipeline.rag_service,
                'search'
            ) as mock_search:
                mock_search.return_value = {
                    "sources": [],
                    "search_metadata": {"total_results": 0}
                }

                await pipeline.process_question(question, context=context)

                # RAG 검색 시 filters 전달 확인
                call_args = mock_search.call_args
                assert call_args is not None
                assert call_args.kwargs.get("filters") == {"stage": "3"}
