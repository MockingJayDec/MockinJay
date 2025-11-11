"""
통합 채팅 API 엔드포인트
"""
from fastapi import APIRouter, HTTPException, status
from backend.schemas.chat import ChatRequest, ChatResponse, ChatError
from backend.services.chat_pipeline import chat_pipeline
from backend.core.logging import logger
import asyncio

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    summary="질문 처리 (통합 파이프라인)",
    description="""
    사용자 질문을 처리하는 End-to-End 파이프라인

    **처리 과정**:
    1. 응급 상황 감지 (최우선)
    2. 의학적 판단 요청 감지
    3. 의도 분류 (LLM)
    4. 벡터 DB 검색 + 외부 API (RESEARCH)
    5. 문서 요약 생성
    6. 안전성 검증
    7. 최종 응답 반환

    **타임아웃**: 30초
    """,
    responses={
        200: {"description": "성공적으로 처리됨"},
        400: {"description": "잘못된 요청"},
        500: {"description": "서버 에러"},
        504: {"description": "타임아웃"}
    }
)
async def process_chat(request: ChatRequest):
    """
    채팅 요청 처리

    Args:
        request: 채팅 요청 (질문, 사용자 ID, 컨텍스트)

    Returns:
        ChatResponse: 최종 응답
    """
    try:
        logger.info(f"Chat request received: {request.question[:50]}...")

        # 타임아웃 30초 설정
        response = await asyncio.wait_for(
            chat_pipeline.process_question(
                question=request.question,
                user_id=request.user_id,
                context=request.context
            ),
            timeout=30.0
        )

        logger.info(f"Chat response generated successfully")
        return response

    except asyncio.TimeoutError:
        logger.error(f"Timeout processing question: {request.question}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="요청 처리 시간이 초과되었습니다. 잠시 후 다시 시도해주세요."
        )
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="요청 처리 중 오류가 발생했습니다."
        )


@router.get(
    "/health",
    summary="채팅 파이프라인 헬스 체크",
    description="채팅 파이프라인의 상태를 확인합니다."
)
async def chat_health():
    """채팅 파이프라인 헬스 체크"""
    try:
        # 간단한 테스트 질문으로 파이프라인 검증
        test_response = await asyncio.wait_for(
            chat_pipeline.process_question(
                question="안녕하세요",
                user_id=None,
                context=None
            ),
            timeout=5.0
        )

        return {
            "status": "healthy",
            "pipeline": "operational",
            "test_response_time": test_response.get("processing_time", 0)
        }
    except Exception as e:
        logger.error(f"Chat pipeline health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "pipeline": "error",
            "error": str(e)
        }
