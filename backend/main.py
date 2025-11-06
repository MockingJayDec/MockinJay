"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from backend.api.v1 import router as api_v1_router
from backend.core.config import settings
from backend.core.logging import setup_logging, logger
from backend.core.errors import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # 시작 시
    logger.info("MockinJay 백엔드 시작...")
    logger.info(f"환경: {settings.ENVIRONMENT}")
    yield
    # 종료 시
    logger.info("MockinJay 백엔드 종료...")


# FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="CKD 환자 지원 AI 챗봇 백엔드",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
)

# 로깅 설정
setup_logging()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 에러 핸들러 설정
setup_exception_handlers(app)

# API 라우터 등록
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health_check():
    """헬스 체크 엔드포인트"""
    return JSONResponse(
        content={
            "status": "healthy",
            "service": "MockinJay Backend",
            "version": "0.1.0",
            "environment": settings.ENVIRONMENT,
        }
    )


@app.get("/", tags=["root"])
async def root():
    """루트 엔드포인트"""
    return {
        "message": "MockinJay API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
