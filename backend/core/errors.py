"""
에러 핸들링 및 커스텀 예외
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import traceback
from backend.core.logging import logger


class MockinJayException(Exception):
    """기본 커스텀 예외"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class IntentClassificationError(MockinJayException):
    """의도 분류 실패"""

    def __init__(self, message: str = "의도 분류에 실패했습니다"):
        super().__init__(message, status_code=500)


class VectorDBError(MockinJayException):
    """벡터 DB 접근 오류"""

    def __init__(self, message: str = "벡터 데이터베이스 오류가 발생했습니다"):
        super().__init__(message, status_code=500)


class LLMAPIError(MockinJayException):
    """LLM API 호출 오류"""

    def __init__(self, message: str = "LLM API 호출에 실패했습니다"):
        super().__init__(message, status_code=503)


class RAGSearchError(MockinJayException):
    """RAG 검색 오류"""

    def __init__(self, message: str = "문서 검색에 실패했습니다"):
        super().__init__(message, status_code=500)


def setup_exception_handlers(app: FastAPI):
    """예외 핸들러 등록"""

    @app.exception_handler(MockinJayException)
    async def mockinjay_exception_handler(request: Request, exc: MockinJayException):
        """커스텀 예외 핸들러"""
        logger.error(f"MockinJayException: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.__class__.__name__,
                "message": exc.message,
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """입력 검증 오류 핸들러"""
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "ValidationError",
                "message": "입력 데이터가 올바르지 않습니다",
                "details": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """일반 예외 핸들러"""
        logger.error(f"Unexpected error: {str(exc)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "InternalServerError",
                "message": "서버 내부 오류가 발생했습니다",
            },
        )
