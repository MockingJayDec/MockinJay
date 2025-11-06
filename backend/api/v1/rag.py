"""
RAG 검색 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from backend.services.rag_search import rag_search_service
from backend.core.logging import logger
import time

router = APIRouter(prefix="/rag", tags=["RAG Search"])


class RAGSearchRequest(BaseModel):
    """RAG 검색 요청"""
    query: str = Field(..., description="검색 쿼리", min_length=1, max_length=500)
    intent: str = Field(..., description="의도 타입 (MEDICAL_INFO, RESEARCH, POLICY 등)")
    top_k: int = Field(default=5, description="반환할 결과 개수", ge=1, le=20)
    filters: Optional[Dict[str, Any]] = Field(default=None, description="메타데이터 필터")
    use_external_api: bool = Field(
        default=False,
        description="외부 API 사용 여부 (RESEARCH 의도의 경우 PubMed API)"
    )


class DocumentResult(BaseModel):
    """문서 검색 결과"""
    id: str = Field(..., description="문서 ID")
    document: str = Field(..., description="문서 내용")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="메타데이터")
    source: str = Field(..., description="출처 (vector_db, pubmed 등)")
    intent: Optional[str] = Field(default=None, description="의도 타입")
    similarity_score: float = Field(..., description="유사도 점수", ge=0.0, le=1.0)


class SearchMetadata(BaseModel):
    """검색 메타데이터"""
    vector_db_used: bool = Field(..., description="벡터 DB 사용 여부")
    external_api_used: bool = Field(..., description="외부 API 사용 여부")
    total_results: int = Field(..., description="전체 결과 개수")
    search_time: float = Field(..., description="검색 소요 시간 (초)")


class RAGSearchResponse(BaseModel):
    """RAG 검색 응답"""
    query: str = Field(..., description="검색 쿼리")
    intent: str = Field(..., description="의도 타입")
    sources: List[DocumentResult] = Field(..., description="검색 결과 리스트")
    search_metadata: SearchMetadata = Field(..., description="검색 메타데이터")


class SearchStatsResponse(BaseModel):
    """검색 통계 응답"""
    intent: str = Field(..., description="의도 타입")
    available_documents: int = Field(..., description="사용 가능한 문서 개수")
    embedding_model: str = Field(..., description="임베딩 모델")
    external_api_available: bool = Field(..., description="외부 API 사용 가능 여부")


@router.post("/search", response_model=RAGSearchResponse)
async def search(request: RAGSearchRequest):
    """
    RAG 검색 수행

    벡터 DB를 통한 문서 검색 및 외부 API 통합 검색을 수행합니다.
    - 벡터 유사도 검색
    - PubMed API 검색 (RESEARCH 의도의 경우)
    - 중복 제거 및 결과 정렬
    """
    start_time = time.time()

    try:
        # RAG 검색 수행
        result = rag_search_service.search(
            query=request.query,
            intent=request.intent,
            top_k=request.top_k,
            filters=request.filters,
            use_external_api=request.use_external_api
        )

        # 에러 체크
        if "error" in result:
            logger.error(f"RAG search error: {result['error']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"검색 중 오류가 발생했습니다: {result['error']}"
            )

        # 검색 시간 계산
        search_time = time.time() - start_time

        # 응답 구성
        response = RAGSearchResponse(
            query=result["query"],
            intent=result["intent"],
            sources=[DocumentResult(**source) for source in result["sources"]],
            search_metadata=SearchMetadata(
                **result["search_metadata"],
                search_time=search_time
            )
        )

        # 성능 체크
        if search_time > 5.0:
            logger.warning(f"RAG search slow: {search_time:.2f}s")

        logger.info(
            f"RAG search completed: {len(result['sources'])} results "
            f"(time: {search_time:.2f}s)"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="검색 중 오류가 발생했습니다"
        )


@router.get("/stats/{intent}", response_model=SearchStatsResponse)
async def get_search_stats(intent: str):
    """
    검색 통계 조회

    특정 의도에 대한 검색 가능한 문서 수 및 설정 정보를 조회합니다.
    """
    try:
        stats = rag_search_service.get_search_stats(intent=intent)

        if "error" in stats:
            logger.error(f"Failed to get search stats: {stats['error']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"통계 조회 중 오류가 발생했습니다: {stats['error']}"
            )

        return SearchStatsResponse(**stats)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="통계 조회 중 오류가 발생했습니다"
        )
