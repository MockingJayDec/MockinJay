"""
API v1 라우터
"""
from fastapi import APIRouter
from backend.api.v1 import intent

# 메인 라우터 생성
router = APIRouter()


# 헬스 체크용 임시 엔드포인트
@router.get("/ping", tags=["health"])
async def ping():
    """API 라우터 연결 확인"""
    return {"message": "pong", "api_version": "v1"}


# Vector DB 라우터 추가
from backend.api.v1 import vector
router.include_router(vector.router)

# 향후 추가될 라우터들
# from backend.api.v1 import rag, feedback
# router.include_router(rag.router)
# router.include_router(feedback.router)
