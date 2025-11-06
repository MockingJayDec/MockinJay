"""
논문/문서 요약 서비스
LLM 기반 의료 문서 요약 및 검증
"""

import logging
from typing import List, Dict, Any, Optional
from backend.services.llm import llm_service
from backend.core.config import settings
import re

logger = logging.getLogger(__name__)


class DocumentSummarizer:
    """
    문서 요약 서비스
    - LLM 기반 요약 생성
    - 병기별 맞춤 설명
    - 의학적 안전성 검증
    """

    def __init__(self):
        """요약 서비스 초기화"""
        logger.info("Document Summarizer initialized")

    def _build_summarization_prompt(
        self,
        document: Dict[str, Any],
        stage: Optional[str] = None
    ) -> str:
        """
        요약 프롬프트 생성

        Args:
            document: 요약할 문서 (제목, 내용, 메타데이터 포함)
            stage: CKD 병기 (1-5, 선택사항)

        Returns:
            요약 프롬프트
        """
        doc_title = document.get('title', '제목 없음')
        doc_content = document.get('document', document.get('content', ''))
        doc_metadata = document.get('metadata', {})

        # 병기별 맞춤 설명 안내
        stage_guidance = ""
        if stage:
            stage_guidance = f"\n\n**중요**: 이 환자는 CKD {stage}기 환자입니다. 이 병기에 맞는 수준으로 설명해주세요."

        prompt = f"""다음 의료 문서를 요약해주세요.

**문서 제목**: {doc_title}

**문서 내용**:
{doc_content}

**메타데이터**:
- 저자: {doc_metadata.get('authors', '알 수 없음')}
- 출판 연도: {doc_metadata.get('year', '알 수 없음')}
- 출처: {doc_metadata.get('source', '알 수 없음')}
{stage_guidance}

아래 형식으로 요약해주세요:

제목: [제목]
저자: [저자]
연도: [연도]
요약: [2-3문장으로 핵심 내용 요약, 평이한 언어 사용]
주요 발견사항:
- [발견사항 1]
- [발견사항 2]
- [발견사항 3]
관련성: [이 연구가 CKD 환자에게 어떤 의미가 있는지 설명]

**제약사항**:
- 요약은 100-150 단어 이내로 작성
- 전문 용어는 평이한 언어로 설명
- 의학적으로 정확하고 객관적인 표현 사용
- 환자가 이해하기 쉽게 작성
- 절대 진단이나 치료를 권장하지 마세요
"""
        return prompt

    def _build_batch_summarization_prompt(
        self,
        documents: List[Dict[str, Any]],
        stage: Optional[str] = None
    ) -> str:
        """
        배치 요약 프롬프트 생성

        Args:
            documents: 요약할 문서 리스트
            stage: CKD 병기

        Returns:
            배치 요약 프롬프트
        """
        stage_guidance = ""
        if stage:
            stage_guidance = f"\n\n**중요**: 이 환자는 CKD {stage}기 환자입니다. 이 병기에 맞는 수준으로 설명해주세요."

        # 문서 목록 생성
        doc_list = []
        for idx, doc in enumerate(documents, 1):
            doc_title = doc.get('title', '제목 없음')
            doc_content = doc.get('document', doc.get('content', ''))[:500]  # 500자로 제한
            doc_metadata = doc.get('metadata', {})

            doc_list.append(f"""
## 문서 {idx}
**제목**: {doc_title}
**저자**: {doc_metadata.get('authors', '알 수 없음')}
**연도**: {doc_metadata.get('year', '알 수 없음')}
**출처**: {doc_metadata.get('source', '알 수 없음')}
**내용 미리보기**: {doc_content}...
""")

        prompt = f"""다음 {len(documents)}개의 의료 문서를 각각 요약해주세요.
{stage_guidance}

{''.join(doc_list)}

각 문서를 아래 형식으로 요약해주세요:

---
### 문서 1
제목: [제목]
저자: [저자]
연도: [연도]
요약: [2-3문장으로 핵심 내용 요약, 평이한 언어 사용]
주요 발견사항:
- [발견사항 1]
- [발견사항 2]
- [발견사항 3]
관련성: [이 연구가 CKD 환자에게 어떤 의미가 있는지 설명]
---

**제약사항**:
- 각 요약은 100-150 단어 이내로 작성
- 전문 용어는 평이한 언어로 설명
- 의학적으로 정확하고 객관적인 표현 사용
- 환자가 이해하기 쉽게 작성
- 절대 진단이나 치료를 권장하지 마세요
"""
        return prompt

    def _validate_summary_safety(self, summary: str) -> Dict[str, Any]:
        """
        요약 안전성 검증

        Args:
            summary: 생성된 요약

        Returns:
            검증 결과 (is_safe, warnings)
        """
        warnings = []

        # 진단/치료 권장 감지
        diagnosis_keywords = [
            r'당신은.*병',
            r'진단.*받으세요',
            r'이 증상은.*병',
            r'.*병으로 판단',
            r'.*치료.*받으세요',
            r'.*약.*복용.*하세요',
            r'.*수술.*받으세요'
        ]

        for pattern in diagnosis_keywords:
            if re.search(pattern, summary, re.IGNORECASE):
                warnings.append(f"진단/치료 권장 의심: '{pattern}'")

        # 응급 상황 부적절한 조언
        emergency_keywords = [
            r'괜찮습니다',
            r'걱정.*않으셔도',
            r'문제.*없습니다',
            r'위험.*없습니다'
        ]

        if any(re.search(pattern, summary, re.IGNORECASE) for pattern in emergency_keywords):
            warnings.append("응급 상황에 부적절한 안심 문구")

        # 안전성 판단
        is_safe = len(warnings) == 0

        return {
            "is_safe": is_safe,
            "warnings": warnings
        }

    def _parse_summary(self, raw_summary: str) -> Dict[str, Any]:
        """
        요약 텍스트 파싱

        Args:
            raw_summary: LLM 생성 요약 텍스트

        Returns:
            구조화된 요약 데이터
        """
        try:
            # 제목 추출
            title_match = re.search(r'제목:\s*(.+)', raw_summary)
            title = title_match.group(1).strip() if title_match else "제목 없음"

            # 저자 추출
            author_match = re.search(r'저자:\s*(.+)', raw_summary)
            authors = author_match.group(1).strip() if author_match else "알 수 없음"

            # 연도 추출
            year_match = re.search(r'연도:\s*(.+)', raw_summary)
            year = year_match.group(1).strip() if year_match else "알 수 없음"

            # 요약 추출
            summary_match = re.search(r'요약:\s*(.+?)(?=주요 발견사항:|관련성:|$)', raw_summary, re.DOTALL)
            summary = summary_match.group(1).strip() if summary_match else ""

            # 주요 발견사항 추출
            findings_match = re.search(r'주요 발견사항:\s*(.+?)(?=관련성:|$)', raw_summary, re.DOTALL)
            findings_text = findings_match.group(1).strip() if findings_match else ""
            findings = [
                line.strip().lstrip('-').strip()
                for line in findings_text.split('\n')
                if line.strip() and line.strip().startswith('-')
            ]

            # 관련성 추출
            relevance_match = re.search(r'관련성:\s*(.+)', raw_summary, re.DOTALL)
            relevance = relevance_match.group(1).strip() if relevance_match else ""

            return {
                "title": title,
                "authors": authors,
                "year": year,
                "summary": summary,
                "key_findings": findings,
                "relevance": relevance
            }

        except Exception as e:
            logger.error(f"Summary parsing failed: {e}")
            return {
                "title": "파싱 실패",
                "authors": "",
                "year": "",
                "summary": raw_summary,
                "key_findings": [],
                "relevance": ""
            }

    async def summarize(
        self,
        document: Dict[str, Any],
        stage: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        단일 문서 요약

        Args:
            document: 요약할 문서
            stage: CKD 병기 (선택사항)
            model: LLM 모델
            temperature: 생성 온도

        Returns:
            요약 결과
        """
        try:
            # 프롬프트 생성
            prompt = self._build_summarization_prompt(document, stage)

            # LLM 호출
            raw_summary = await llm_service.chat_completion(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=800,
                provider="openai"
            )

            # 요약 파싱
            parsed_summary = self._parse_summary(raw_summary)

            # 안전성 검증
            safety_check = self._validate_summary_safety(raw_summary)

            # 출처 정보 추가
            source_info = {
                "doi": document.get('metadata', {}).get('doi', ''),
                "pubmed_id": document.get('metadata', {}).get('pubmed_id', ''),
                "url": document.get('metadata', {}).get('url', ''),
                "source": document.get('metadata', {}).get('source', '')
            }

            result = {
                **parsed_summary,
                "source": source_info,
                "safety_check": safety_check,
                "stage_customized": stage is not None
            }

            logger.info(f"Document summarized: {parsed_summary['title']}")

            return result

        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return {
                "title": "요약 실패",
                "authors": "",
                "year": "",
                "summary": f"요약 생성 중 오류 발생: {str(e)}",
                "key_findings": [],
                "relevance": "",
                "source": {},
                "safety_check": {"is_safe": False, "warnings": ["요약 생성 실패"]},
                "error": str(e)
            }

    async def batch_summarize(
        self,
        documents: List[Dict[str, Any]],
        stage: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        배치 문서 요약

        Args:
            documents: 요약할 문서 리스트 (최대 5개)
            stage: CKD 병기
            model: LLM 모델
            temperature: 생성 온도

        Returns:
            요약 결과 리스트
        """
        try:
            # 문서 개수 제한
            if len(documents) > 5:
                logger.warning(f"Too many documents: {len(documents)}, limiting to 5")
                documents = documents[:5]

            # 배치 프롬프트 생성
            prompt = self._build_batch_summarization_prompt(documents, stage)

            # LLM 호출
            raw_summary = await llm_service.chat_completion(
                prompt=prompt,
                model=model,
                temperature=temperature,
                max_tokens=3000,
                provider="openai"
            )

            # 요약 분리 (각 문서별)
            summary_sections = re.split(r'---+\s*\n', raw_summary)
            summary_sections = [s.strip() for s in summary_sections if s.strip()]

            results = []

            for idx, doc in enumerate(documents):
                try:
                    # 해당 문서의 요약 추출
                    if idx < len(summary_sections):
                        section = summary_sections[idx]
                    else:
                        # 요약이 부족한 경우 개별 요약 수행
                        logger.warning(f"Missing summary for document {idx}, falling back to individual summarization")
                        return await self.summarize(doc, stage, model, temperature)

                    # 요약 파싱
                    parsed_summary = self._parse_summary(section)

                    # 안전성 검증
                    safety_check = self._validate_summary_safety(section)

                    # 출처 정보 추가
                    source_info = {
                        "doi": doc.get('metadata', {}).get('doi', ''),
                        "pubmed_id": doc.get('metadata', {}).get('pubmed_id', ''),
                        "url": doc.get('metadata', {}).get('url', ''),
                        "source": doc.get('metadata', {}).get('source', '')
                    }

                    result = {
                        **parsed_summary,
                        "source": source_info,
                        "safety_check": safety_check,
                        "stage_customized": stage is not None
                    }

                    results.append(result)

                except Exception as e:
                    logger.error(f"Failed to parse summary for document {idx}: {e}")
                    results.append({
                        "title": "요약 파싱 실패",
                        "authors": "",
                        "year": "",
                        "summary": "요약 생성 중 오류 발생",
                        "key_findings": [],
                        "relevance": "",
                        "source": {},
                        "safety_check": {"is_safe": False, "warnings": ["파싱 실패"]},
                        "error": str(e)
                    })

            logger.info(f"Batch summarization completed: {len(results)} summaries")

            return results

        except Exception as e:
            logger.error(f"Batch summarization failed: {e}")
            # 개별 요약으로 폴백
            logger.info("Falling back to individual summarization")
            results = []
            for doc in documents:
                result = await self.summarize(doc, stage, model, temperature)
                results.append(result)
            return results


# 싱글톤 인스턴스
document_summarizer = DocumentSummarizer()
