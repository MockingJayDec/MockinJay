"""
문서 요약 API 엔드포인트
POST /api/v1/summarize - 문서 요약 생성
"""

from fastapi import APIRouter, HTTPException, status
from backend.schemas.summarizer import (
    SummarizeRequest,
    SummarizeResponse,
    SummaryResult,
    SourceInfo,
    SafetyCheck
)
from backend.services.summarizer import document_summarizer
from backend.core.logging import logger
import time

router = APIRouter(prefix="/summarize", tags=["summarizer"])


@router.post(
    "",
    response_model=SummarizeResponse,
    summary="문서 요약 생성",
    description="논문/문서를 요약하고 안전성을 검증합니다 (최대 5개)"
)
async def summarize_documents(request: SummarizeRequest):
    """
    문서 요약 API

    **요청 본문**:
    - documents: 요약할 문서 리스트 (1-5개)
    - stage: CKD 병기 (선택사항, 1-5)
    - model: LLM 모델 (기본값: gpt-4o-mini)
    - temperature: 생성 온도 (기본값: 0.3)

    **응답**:
    - summaries: 요약 결과 리스트
    - total_documents: 총 문서 수
    - safe_summaries: 안전한 요약 수
    - metadata: 처리 메타데이터

    **제약사항**:
    - 최대 5개 문서까지 처리 가능
    - 각 요약은 100-150 단어 이내
    - 안전하지 않은 요약은 경고 메시지 포함
    """
    try:
        start_time = time.time()

        logger.info(
            f"Summarization request: {len(request.documents)} documents, "
            f"stage={request.stage}, model={request.model}"
        )

        # 문서 데이터 준비
        documents_data = []
        for doc in request.documents:
            doc_dict = {
                "title": doc.title,
                "document": doc.content,
                "metadata": doc.metadata or {}
            }
            documents_data.append(doc_dict)

        # 배치 요약 수행
        summaries = await document_summarizer.batch_summarize(
            documents=documents_data,
            stage=request.stage,
            model=request.model,
            temperature=request.temperature
        )

        # 응답 데이터 구성
        summary_results = []
        safe_count = 0

        for summary in summaries:
            # 안전성 체크
            safety_check = SafetyCheck(**summary["safety_check"])
            if safety_check.is_safe:
                safe_count += 1

            # 출처 정보
            source_info = SourceInfo(**summary["source"])

            # 요약 결과
            result = SummaryResult(
                title=summary["title"],
                authors=summary["authors"],
                year=summary["year"],
                summary=summary["summary"],
                key_findings=summary["key_findings"],
                relevance=summary["relevance"],
                source=source_info,
                safety_check=safety_check,
                stage_customized=summary.get("stage_customized", False),
                error=summary.get("error")
            )

            summary_results.append(result)

        # 처리 시간 계산
        processing_time = time.time() - start_time

        # 메타데이터
        metadata = {
            "processing_time": round(processing_time, 2),
            "model_used": request.model,
            "temperature": request.temperature,
            "stage_customized": request.stage is not None
        }

        response = SummarizeResponse(
            summaries=summary_results,
            total_documents=len(summary_results),
            safe_summaries=safe_count,
            metadata=metadata
        )

        logger.info(
            f"Summarization completed: {len(summary_results)} summaries, "
            f"{safe_count} safe, {processing_time:.2f}s"
        )

        return response

    except Exception as e:
        logger.error(f"Summarization request failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"요약 생성 실패: {str(e)}"
        )


@router.get(
    "/health",
    summary="요약 서비스 상태 확인",
    description="요약 서비스의 상태를 확인합니다"
)
async def health_check():
    """
    요약 서비스 헬스 체크

    **응답**:
    - status: 서비스 상태
    - service: 서비스 이름
    """
    return {
        "status": "healthy",
        "service": "document_summarizer",
        "description": "LLM-based document summarization service"
    }
