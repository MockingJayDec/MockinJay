"""
채팅 엔드포인트 스키마
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatRequest(BaseModel):
    """채팅 요청"""
    question: str = Field(
        ...,
        description="사용자 질문",
        min_length=1,
        max_length=1000
    )
    user_id: Optional[str] = Field(
        None,
        description="사용자 ID (건강 기록용)"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="추가 컨텍스트 (병기, 이전 대화 등)"
    )


class DocumentMetadata(BaseModel):
    """문서 메타데이터"""
    source: str = Field(..., description="출처 (qna, paper, policy)")
    title: Optional[str] = Field(None, description="제목")
    authors: Optional[List[str]] = Field(None, description="저자")
    year: Optional[int] = Field(None, description="연도")
    doi: Optional[str] = Field(None, description="DOI")
    url: Optional[str] = Field(None, description="URL")
    similarity_score: Optional[float] = Field(None, description="유사도 점수")


class SummaryItem(BaseModel):
    """요약 항목"""
    title: str = Field(..., description="제목")
    summary: str = Field(..., description="요약 내용")
    key_findings: List[str] = Field(default_factory=list, description="주요 발견사항")
    relevance: str = Field(..., description="질의와의 관련성")
    metadata: DocumentMetadata


class ChatResponse(BaseModel):
    """채팅 응답"""
    question: str = Field(..., description="원본 질문")
    intent: str = Field(..., description="감지된 의도")
    intent_confidence: float = Field(..., description="의도 분류 신뢰도")

    # 응답 내용
    answer: str = Field(..., description="최종 응답")
    summaries: List[SummaryItem] = Field(default_factory=list, description="관련 문서 요약")

    # 메타데이터
    selected_databases: List[str] = Field(default_factory=list, description="검색된 DB")
    total_documents: int = Field(0, description="검색된 문서 수")
    processing_time: float = Field(..., description="처리 시간 (초)")

    # 안전장치
    is_emergency: bool = Field(False, description="응급 상황 여부")
    is_medical_judgment: bool = Field(False, description="의학적 판단 요청 여부")
    is_safe: bool = Field(True, description="안전성 검증 통과 여부")

    timestamp: datetime = Field(default_factory=datetime.now, description="응답 시각")


class ChatError(BaseModel):
    """채팅 에러"""
    error: str = Field(..., description="에러 유형")
    message: str = Field(..., description="에러 메시지")
    question: str = Field(..., description="원본 질문")
    timestamp: datetime = Field(default_factory=datetime.now, description="에러 시각")
