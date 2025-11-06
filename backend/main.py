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
    description="""
## MockinJay - CKD 환자 지원 AI 챗봇 백엔드 API

만성 콩팥병(CKD) 환자를 위한 AI 기반 의료 정보 제공 시스템입니다.

### 주요 기능

- **🎯 질문 의도 분류**: 9가지 의도 자동 분류 (MEDICAL_INFO, POLICY, WELFARE_INFO 등)
- **🔍 RAG 검색**: Vector DB 기반 의료 논문 검색
- **📝 문서 요약**: LLM 기반 의료 논문 요약 생성
- **💬 통합 챗봇**: End-to-End 질의응답 파이프라인
- **📊 성능 모니터링**: 응답 시간, 정확도, 에러율 추적

### 안전 장치

- **🚨 응급 상황 감지**: 즉시 119/응급실 안내
- **⚕️ 의료 판단 차단**: 진단/처방 질문 차단
- **✅ 비윤리적 질문 필터링**: 부적절한 요청 차단

### 지원 의도 (Intent)

1. **MEDICAL_INFO**: 의학 정보 (질병, 검사, 약물)
2. **POLICY**: 의료 정책 및 가이드라인
3. **WELFARE_INFO**: 복지 정보 (추후 지원)
4. **DIET_INFO**: 식단 정보 (추후 지원)
5. **LEARNING**: 퀴즈 학습 (추후 지원)
6. **HEALTH_RECORD**: 건강 기록 (추후 지원)
7. **CHIT_CHAT**: 일상 대화
8. **NON_MEDICAL**: 의료 외 질문
9. **NON_ETHICAL**: 비윤리적 질문

### 기술 스택

- **Framework**: FastAPI + Pydantic
- **LLM**: OpenAI GPT-4o / Anthropic Claude 3.5 Sonnet
- **Vector DB**: Qdrant
- **Cache**: Redis
- **Embedding**: OpenAI text-embedding-3-small

### 성능 목표

- **응답 시간**: P95 < 25초
- **의도 분류 정확도**: ≥ 90%
- **시스템 에러율**: < 1%
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    contact={
        "name": "MockinJay Team",
        "url": "https://github.com/MockingJayDec/MockinJay",
        "email": "contact@mockinjay.dev",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
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
