"""
Vector Database API 엔드포인트
ChromaDB를 사용한 벡터 검색 및 관리
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from backend.services.vector_db import vector_db
from backend.services.data_loader import data_loader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/vector", tags=["Vector Database"])


# Request/Response Models
class DocumentInput(BaseModel):
    """문서 입력 모델"""
    intent: str = Field(..., description="의도 타입 (MEDICAL_INFO, RESEARCH, POLICY 등)")
    documents: List[str] = Field(..., description="저장할 문서 리스트")
    metadatas: Optional[List[Dict[str, Any]]] = Field(None, description="문서 메타데이터")
    ids: Optional[List[str]] = Field(None, description="문서 ID (선택사항)")

    class Config:
        schema_extra = {
            "example": {
                "intent": "MEDICAL_INFO",
                "documents": [
                    "질문: GFR이란? 답변: 신장 기능 지표입니다.",
                    "질문: 크레아티닌 정상치? 답변: 0.6-1.2 mg/dL"
                ],
                "metadatas": [
                    {"category": "검사", "stage": "all"},
                    {"category": "검사", "stage": "all"}
                ]
            }
        }


class SearchRequest(BaseModel):
    """검색 요청 모델"""
    intent: str = Field(..., description="검색할 의도 타입")
    query: str = Field(..., description="검색 쿼리")
    top_k: int = Field(5, ge=1, le=20, description="반환할 결과 개수")
    filters: Optional[Dict[str, Any]] = Field(None, description="메타데이터 필터")

    class Config:
        schema_extra = {
            "example": {
                "intent": "MEDICAL_INFO",
                "query": "크레아티닌 수치가 높으면 어떻게 해야 하나요?",
                "top_k": 5,
                "filters": {"category": "검사"}
            }
        }


class SearchResult(BaseModel):
    """검색 결과 모델"""
    id: str
    document: str
    metadata: Dict[str, Any]
    similarity_score: float


class UpdateRequest(BaseModel):
    """문서 업데이트 요청"""
    intent: str
    document_id: str
    document: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class DeleteRequest(BaseModel):
    """문서 삭제 요청"""
    intent: str
    document_ids: List[str]


# API Endpoints
@router.post("/add", summary="문서 추가")
async def add_documents(request: DocumentInput):
    """
    벡터 데이터베이스에 문서 추가
    """
    try:
        success = vector_db.add_documents(
            intent=request.intent,
            documents=request.documents,
            metadatas=request.metadatas,
            ids=request.ids
        )

        if success:
            return {
                "status": "success",
                "message": f"Successfully added {len(request.documents)} documents",
                "intent": request.intent
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to add documents")

    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=List[SearchResult], summary="유사도 검색")
async def search_documents(request: SearchRequest):
    """
    의도별 벡터 데이터베이스 검색
    """
    try:
        results = vector_db.search(
            intent=request.intent,
            query=request.query,
            top_k=request.top_k,
            filters=request.filters
        )

        return results

    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/update", summary="문서 업데이트")
async def update_document(request: UpdateRequest):
    """
    기존 문서 업데이트
    """
    try:
        success = vector_db.update_document(
            intent=request.intent,
            document_id=request.document_id,
            document=request.document,
            metadata=request.metadata
        )

        if success:
            return {
                "status": "success",
                "message": f"Document {request.document_id} updated"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update document")

    except Exception as e:
        logger.error(f"Update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete", summary="문서 삭제")
async def delete_documents(request: DeleteRequest):
    """
    문서 삭제
    """
    try:
        success = vector_db.delete_documents(
            intent=request.intent,
            document_ids=request.document_ids
        )

        if success:
            return {
                "status": "success",
                "message": f"Deleted {len(request.document_ids)} documents"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete documents")

    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{intent}", summary="컬렉션 통계")
async def get_collection_stats(intent: str):
    """
    특정 의도의 컬렉션 통계 조회
    """
    try:
        stats = vector_db.get_collection_stats(intent)
        return stats

    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset/{intent}", summary="컬렉션 초기화")
async def reset_collection(intent: str):
    """
    특정 의도의 컬렉션 초기화 (모든 데이터 삭제)
    """
    try:
        success = vector_db.reset_collection(intent)

        if success:
            return {
                "status": "success",
                "message": f"Collection for {intent} has been reset"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to reset collection")

    except Exception as e:
        logger.error(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load-sample-data", summary="샘플 데이터 로드")
async def load_sample_data(
    data_type: str = Query("all", enum=["all", "medical_qa", "research_papers", "policy_guidelines"])
):
    """
    샘플 데이터를 벡터 데이터베이스에 로드

    Parameters:
        data_type: 로드할 데이터 타입 (all, medical_qa, research_papers, policy_guidelines)
    """
    try:
        if data_type == "all":
            results = data_loader.load_all_sample_data()
        elif data_type == "medical_qa":
            results = {"medical_qa": data_loader.load_sample_medical_qa()}
        elif data_type == "research_papers":
            results = {"research_papers": data_loader.load_sample_research_papers()}
        elif data_type == "policy_guidelines":
            results = {"policy_guidelines": data_loader.load_sample_policy_guidelines()}
        else:
            raise HTTPException(status_code=400, detail="Invalid data type")

        # 결과 확인
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)

        if success_count == total_count:
            return {
                "status": "success",
                "message": f"Successfully loaded all {total_count} data types",
                "details": results
            }
        elif success_count > 0:
            return {
                "status": "partial_success",
                "message": f"Loaded {success_count}/{total_count} data types",
                "details": results
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to load sample data")

    except Exception as e:
        logger.error(f"Sample data loading error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/available-intents", summary="사용 가능한 의도 목록")
async def get_available_intents():
    """
    사용 가능한 의도(컬렉션) 목록 조회
    """
    try:
        intents = list(vector_db.collections.keys())
        stats = []

        for intent in intents:
            stat = vector_db.get_collection_stats(intent)
            stats.append(stat)

        return {
            "intents": intents,
            "collections": stats,
            "total_collections": len(intents)
        }

    except Exception as e:
        logger.error(f"Error getting intents: {e}")
        raise HTTPException(status_code=500, detail=str(e))