"""
RAG (Retrieval-Augmented Generation) Search Service
벡터 DB 검색과 외부 API 통합을 통한 문서 검색 서비스
"""

import logging
from typing import List, Dict, Any, Optional
from backend.services.vector_db import vector_db
from backend.services.cache import cache_service
from backend.core.config import settings

logger = logging.getLogger(__name__)


class RAGSearchService:
    """
    RAG 검색 서비스
    - 벡터 DB 검색
    - PubMed API 통합 (RESEARCH 의도)
    - 중복 제거 및 결과 정렬
    """

    def __init__(self):
        """RAG 검색 서비스 초기화"""
        self.vector_db = vector_db
        self.cache = cache_service
        logger.info("RAG Search Service initialized")

    def search(
        self,
        query: str,
        intent: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        use_external_api: bool = False
    ) -> Dict[str, Any]:
        """
        통합 검색 수행

        Args:
            query: 검색 쿼리
            intent: 의도 타입 (MEDICAL_INFO, RESEARCH, POLICY 등)
            top_k: 반환할 결과 개수
            filters: 메타데이터 필터
            use_external_api: 외부 API 사용 여부 (RESEARCH 의도 전용)

        Returns:
            검색 결과 딕셔너리
        """
        try:
            # 1. 캐시 확인 (외부 API를 사용하지 않고 필터가 없는 경우만)
            if not use_external_api and not filters:
                cached_result = self.cache.get_rag_cache(
                    query=query,
                    intent=intent,
                    top_k=top_k
                )
                if cached_result:
                    cached_result["search_metadata"]["from_cache"] = True
                    logger.info(f"Cache hit for query: {query}")
                    return cached_result

            results = {
                "query": query,
                "intent": intent,
                "sources": [],
                "search_metadata": {
                    "vector_db_used": True,
                    "external_api_used": False,
                    "total_results": 0,
                    "from_cache": False
                }
            }

            # 1. 벡터 DB 검색
            vector_results = self._search_vector_db(
                intent=intent,
                query=query,
                top_k=top_k,
                filters=filters
            )

            results["sources"].extend(vector_results)
            results["search_metadata"]["total_results"] = len(vector_results)

            # 2. RESEARCH 의도의 경우 PubMed API 추가 검색 (선택적)
            if intent == "RESEARCH" and use_external_api:
                pubmed_results = self._search_pubmed(query=query, max_results=top_k)

                if pubmed_results:
                    results["sources"].extend(pubmed_results)
                    results["search_metadata"]["external_api_used"] = True
                    results["search_metadata"]["total_results"] += len(pubmed_results)

            # 3. 중복 제거 및 정렬
            results["sources"] = self._deduplicate_and_sort(
                results["sources"],
                top_k=top_k
            )
            results["search_metadata"]["total_results"] = len(results["sources"])

            # 4. 캐시에 저장 (외부 API를 사용하지 않고 필터가 없는 경우만)
            if not use_external_api and not filters:
                self.cache.set_rag_cache(
                    query=query,
                    intent=intent,
                    top_k=top_k,
                    result=results,
                    ttl=86400  # 24시간
                )

            logger.info(
                f"Search completed for intent '{intent}': "
                f"{results['search_metadata']['total_results']} results"
            )

            return results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return {
                "query": query,
                "intent": intent,
                "sources": [],
                "error": str(e),
                "search_metadata": {
                    "vector_db_used": False,
                    "external_api_used": False,
                    "total_results": 0
                }
            }

    def _search_vector_db(
        self,
        intent: str,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        벡터 DB 검색 수행

        Args:
            intent: 의도 타입
            query: 검색 쿼리
            top_k: 반환할 결과 개수
            filters: 메타데이터 필터

        Returns:
            검색 결과 리스트
        """
        try:
            # VectorDBService의 search 메서드 호출
            results = self.vector_db.search(
                intent=intent,
                query=query,
                top_k=top_k,
                filters=filters
            )

            # 결과 포맷 통일 (source 필드 추가)
            for result in results:
                result['source'] = 'vector_db'
                result['intent'] = intent

            return results

        except Exception as e:
            logger.error(f"Vector DB search failed: {e}")
            return []

    def _search_pubmed(
        self,
        query: str,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        PubMed API 검색 (RESEARCH 의도 전용)

        Args:
            query: 검색 쿼리
            max_results: 최대 결과 개수

        Returns:
            PubMed 검색 결과 리스트
        """
        try:
            from backend.services.pubmed_client import pubmed_client

            logger.info(f"PubMed search requested for: {query}")

            # PubMed API 검색 수행
            results = pubmed_client.search(query=query, max_results=max_results)

            return results

        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return []

    def _deduplicate_and_sort(
        self,
        results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        중복 제거 및 유사도 점수로 정렬

        Args:
            results: 검색 결과 리스트
            top_k: 반환할 최대 결과 개수

        Returns:
            중복 제거 및 정렬된 결과 리스트
        """
        try:
            # 1. 중복 제거 (document 내용 기준)
            seen = set()
            unique_results = []

            for result in results:
                doc_content = result.get('document', '')

                # 문서 내용의 해시값으로 중복 체크
                doc_hash = hash(doc_content)

                if doc_hash not in seen:
                    seen.add(doc_hash)
                    unique_results.append(result)

            # 2. 유사도 점수로 정렬 (내림차순)
            sorted_results = sorted(
                unique_results,
                key=lambda x: x.get('similarity_score', 0),
                reverse=True
            )

            # 3. Top-K 결과만 반환
            return sorted_results[:top_k]

        except Exception as e:
            logger.error(f"Deduplication and sorting failed: {e}")
            return results[:top_k]

    def get_search_stats(self, intent: str) -> Dict[str, Any]:
        """
        검색 통계 조회

        Args:
            intent: 의도 타입

        Returns:
            검색 관련 통계 정보
        """
        try:
            # 벡터 DB 통계 조회
            db_stats = self.vector_db.get_collection_stats(intent)

            return {
                "intent": intent,
                "available_documents": db_stats.get('document_count', 0),
                "embedding_model": db_stats.get('embedding_model', 'unknown'),
                "external_api_available": intent == "RESEARCH"
            }

        except Exception as e:
            logger.error(f"Failed to get search stats: {e}")
            return {"error": str(e)}


# 싱글톤 인스턴스
rag_search_service = RAGSearchService()
