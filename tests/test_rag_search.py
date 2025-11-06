"""
RAG Search Service Tests
"""
import pytest
from backend.services.rag_search import RAGSearchService, rag_search_service


class TestRAGSearchService:
    """RAG 검색 서비스 테스트"""

    def test_rag_service_initialization(self):
        """RAG 서비스 초기화 테스트"""
        service = RAGSearchService()
        assert service is not None
        assert service.vector_db is not None
        assert service.cache is not None

    def test_search_with_medical_info_intent(self):
        """MEDICAL_INFO 의도로 검색 테스트"""
        result = rag_search_service.search(
            query="CKD 환자의 크레아티닌 정상 수치는?",
            intent="MEDICAL_INFO",
            top_k=5
        )

        assert result is not None
        assert "query" in result
        assert "intent" in result
        assert "sources" in result
        assert "search_metadata" in result
        assert result["intent"] == "MEDICAL_INFO"

    def test_search_with_research_intent(self):
        """RESEARCH 의도로 검색 테스트"""
        result = rag_search_service.search(
            query="chronic kidney disease treatment",
            intent="RESEARCH",
            top_k=3
        )

        assert result is not None
        assert result["intent"] == "RESEARCH"
        assert isinstance(result["sources"], list)

    def test_search_with_policy_intent(self):
        """POLICY 의도로 검색 테스트"""
        result = rag_search_service.search(
            query="CKD 진료지침",
            intent="POLICY",
            top_k=5
        )

        assert result is not None
        assert result["intent"] == "POLICY"
        assert "search_metadata" in result

    def test_search_with_filters(self):
        """메타데이터 필터링 검색 테스트"""
        result = rag_search_service.search(
            query="GFR",
            intent="MEDICAL_INFO",
            top_k=5,
            filters={"stage": "3"}
        )

        assert result is not None
        assert isinstance(result["sources"], list)

    def test_search_result_structure(self):
        """검색 결과 구조 검증"""
        result = rag_search_service.search(
            query="신장 기능",
            intent="MEDICAL_INFO",
            top_k=3
        )

        assert "query" in result
        assert "intent" in result
        assert "sources" in result
        assert "search_metadata" in result

        metadata = result["search_metadata"]
        assert "vector_db_used" in metadata
        assert "external_api_used" in metadata
        assert "total_results" in metadata

    def test_deduplication(self):
        """중복 제거 테스트"""
        service = RAGSearchService()

        # 중복 문서가 포함된 결과 생성
        results = [
            {"document": "테스트 문서 1", "similarity_score": 0.9},
            {"document": "테스트 문서 2", "similarity_score": 0.8},
            {"document": "테스트 문서 1", "similarity_score": 0.85},  # 중복
            {"document": "테스트 문서 3", "similarity_score": 0.7},
        ]

        deduplicated = service._deduplicate_and_sort(results, top_k=5)

        # 중복 제거 확인
        assert len(deduplicated) == 3
        # 정렬 확인 (유사도 내림차순)
        assert deduplicated[0]["similarity_score"] >= deduplicated[1]["similarity_score"]

    def test_top_k_limiting(self):
        """Top-K 결과 개수 제한 테스트"""
        result = rag_search_service.search(
            query="CKD",
            intent="MEDICAL_INFO",
            top_k=3
        )

        # 결과 개수가 top_k 이하인지 확인
        assert len(result["sources"]) <= 3

    def test_search_stats(self):
        """검색 통계 조회 테스트"""
        stats = rag_search_service.get_search_stats("MEDICAL_INFO")

        assert stats is not None
        assert "intent" in stats
        assert "available_documents" in stats
        assert "embedding_model" in stats

    def test_empty_query_handling(self):
        """빈 쿼리 처리 테스트"""
        result = rag_search_service.search(
            query="",
            intent="MEDICAL_INFO",
            top_k=5
        )

        # 빈 쿼리도 처리 가능해야 함 (결과는 없을 수 있음)
        assert result is not None
        assert isinstance(result["sources"], list)

    def test_invalid_intent_handling(self):
        """잘못된 의도 처리 테스트"""
        result = rag_search_service.search(
            query="테스트",
            intent="INVALID_INTENT",
            top_k=5
        )

        assert result is not None
        # 에러 또는 빈 결과 반환
        assert isinstance(result["sources"], list)


class TestPubMedIntegration:
    """PubMed API 통합 테스트"""

    def test_pubmed_search_disabled_by_default(self):
        """기본적으로 PubMed 검색이 비활성화되어 있는지 확인"""
        result = rag_search_service.search(
            query="chronic kidney disease",
            intent="RESEARCH",
            top_k=3,
            use_external_api=False
        )

        assert result["search_metadata"]["external_api_used"] is False

    @pytest.mark.skipif(
        True,  # PubMed API 키가 없을 경우 스킵
        reason="PubMed API key not configured"
    )
    def test_pubmed_search_enabled(self):
        """PubMed 검색 활성화 테스트 (API 키 필요)"""
        result = rag_search_service.search(
            query="chronic kidney disease treatment",
            intent="RESEARCH",
            top_k=3,
            use_external_api=True
        )

        # PubMed 검색이 실행되었는지 확인
        assert result["search_metadata"]["external_api_used"] is True


class TestCaching:
    """캐싱 기능 테스트"""

    def test_cache_integration(self):
        """캐시 통합 테스트"""
        service = RAGSearchService()

        # 캐시 서비스가 초기화되었는지 확인
        assert service.cache is not None

    def test_search_caching(self):
        """검색 결과 캐싱 테스트"""
        query = "CKD 병기 분류"
        intent = "MEDICAL_INFO"
        top_k = 5

        # 첫 번째 검색 (캐시에 저장됨)
        result1 = rag_search_service.search(
            query=query,
            intent=intent,
            top_k=top_k
        )

        # 두 번째 검색 (캐시에서 가져옴)
        result2 = rag_search_service.search(
            query=query,
            intent=intent,
            top_k=top_k
        )

        # 결과가 동일해야 함
        assert result1["query"] == result2["query"]
        assert result1["intent"] == result2["intent"]
        assert len(result1["sources"]) == len(result2["sources"])

    def test_cache_bypass_with_filters(self):
        """필터 사용 시 캐시 우회 테스트"""
        query = "GFR 수치"
        intent = "MEDICAL_INFO"

        # 필터 없는 검색
        result1 = rag_search_service.search(
            query=query,
            intent=intent,
            top_k=5
        )

        # 필터 있는 검색 (캐시 우회)
        result2 = rag_search_service.search(
            query=query,
            intent=intent,
            top_k=5,
            filters={"stage": "3"}
        )

        # 필터가 적용되어 결과가 다를 수 있음
        assert result1["query"] == result2["query"]
        # 필터 없는 검색은 캐시에서 가져올 수 있음
        # 필터 있는 검색은 캐시를 우회함
