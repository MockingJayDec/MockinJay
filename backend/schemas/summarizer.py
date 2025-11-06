"""
문서 요약 API 스키마
Pydantic 모델 정의
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class DocumentInput(BaseModel):
    """입력 문서 모델"""
    title: str = Field(..., description="문서 제목")
    content: str = Field(..., description="문서 내용", alias="document")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="문서 메타데이터")

    class Config:
        populate_by_name = True  # alias와 필드명 모두 허용


class SummarizeRequest(BaseModel):
    """요약 요청 모델"""
    documents: List[DocumentInput] = Field(
        ...,
        min_length=1,
        max_length=5,
        description="요약할 문서 리스트 (최대 5개)"
    )
    stage: Optional[str] = Field(
        None,
        pattern="^[1-5]$",
        description="CKD 병기 (1-5)"
    )
    model: str = Field(
        default="gpt-4o-mini",
        description="사용할 LLM 모델"
    )
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="생성 온도 (0.0-1.0)"
    )


class SourceInfo(BaseModel):
    """출처 정보"""
    doi: str = Field(default="", description="DOI")
    pubmed_id: str = Field(default="", description="PubMed ID")
    url: str = Field(default="", description="URL")
    source: str = Field(default="", description="출처")


class SafetyCheck(BaseModel):
    """안전성 검증 결과"""
    is_safe: bool = Field(..., description="안전 여부")
    warnings: List[str] = Field(default=[], description="경고 메시지 리스트")


class SummaryResult(BaseModel):
    """요약 결과"""
    title: str = Field(..., description="문서 제목")
    authors: str = Field(..., description="저자")
    year: str = Field(..., description="출판 연도")
    summary: str = Field(..., description="요약 (2-3문장)")
    key_findings: List[str] = Field(default=[], description="주요 발견사항")
    relevance: str = Field(..., description="CKD 환자와의 관련성")
    source: SourceInfo = Field(..., description="출처 정보")
    safety_check: SafetyCheck = Field(..., description="안전성 검증 결과")
    stage_customized: bool = Field(default=False, description="병기별 맞춤 여부")
    error: Optional[str] = Field(None, description="오류 메시지")


class SummarizeResponse(BaseModel):
    """요약 응답 모델"""
    summaries: List[SummaryResult] = Field(..., description="요약 결과 리스트")
    total_documents: int = Field(..., description="총 문서 수")
    safe_summaries: int = Field(..., description="안전한 요약 수")
    metadata: Dict[str, Any] = Field(default={}, description="메타데이터")
