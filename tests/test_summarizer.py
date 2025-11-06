"""
문서 요약 서비스 테스트
"""

import pytest
from backend.services.summarizer import document_summarizer


class TestDocumentSummarizer:
    """문서 요약 서비스 테스트"""

    def test_summarizer_initialization(self):
        """요약 서비스 초기화 테스트"""
        assert document_summarizer is not None

    def test_build_summarization_prompt(self):
        """요약 프롬프트 생성 테스트"""
        document = {
            "title": "CKD 환자의 혈압 관리",
            "document": "CKD 환자에서 혈압 관리는 매우 중요합니다. 목표 혈압은 130/80 mmHg 이하입니다.",
            "metadata": {
                "authors": "홍길동",
                "year": "2024",
                "source": "대한신장학회지"
            }
        }

        prompt = document_summarizer._build_summarization_prompt(document)

        assert "CKD 환자의 혈압 관리" in prompt
        assert "홍길동" in prompt
        assert "2024" in prompt
        assert "100-150 단어" in prompt

    def test_build_summarization_prompt_with_stage(self):
        """병기별 맞춤 프롬프트 생성 테스트"""
        document = {
            "title": "테스트 문서",
            "document": "테스트 내용",
            "metadata": {}
        }

        prompt = document_summarizer._build_summarization_prompt(document, stage="3")

        assert "CKD 3기" in prompt

    def test_build_batch_summarization_prompt(self):
        """배치 요약 프롬프트 생성 테스트"""
        documents = [
            {
                "title": "문서 1",
                "document": "내용 1",
                "metadata": {"authors": "저자1", "year": "2024"}
            },
            {
                "title": "문서 2",
                "document": "내용 2",
                "metadata": {"authors": "저자2", "year": "2023"}
            }
        ]

        prompt = document_summarizer._build_batch_summarization_prompt(documents)

        assert "2개의 의료 문서" in prompt
        assert "문서 1" in prompt
        assert "문서 2" in prompt

    def test_validate_summary_safety_safe(self):
        """안전한 요약 검증 테스트"""
        safe_summary = """
제목: CKD 환자의 혈압 관리
저자: 홍길동
연도: 2024
요약: 이 연구는 CKD 환자의 혈압 관리에 대해 다룹니다. 목표 혈압은 130/80 mmHg 이하로 권장됩니다.
주요 발견사항:
- 혈압 조절이 중요함
- 약물 치료 필요
- 정기적인 모니터링 권장
관련성: CKD 환자의 혈압 관리는 질병 진행을 늦추는 데 중요합니다.
"""

        result = document_summarizer._validate_summary_safety(safe_summary)

        assert result["is_safe"] is True
        assert len(result["warnings"]) == 0

    def test_validate_summary_safety_unsafe_diagnosis(self):
        """진단 권장이 있는 요약 검증 테스트"""
        unsafe_summary = """
제목: 테스트
요약: 당신은 CKD 3기 병으로 진단받으세요.
"""

        result = document_summarizer._validate_summary_safety(unsafe_summary)

        assert result["is_safe"] is False
        assert len(result["warnings"]) > 0

    def test_validate_summary_safety_unsafe_treatment(self):
        """치료 권장이 있는 요약 검증 테스트"""
        unsafe_summary = """
제목: 테스트
요약: 이 약을 복용하세요.
"""

        result = document_summarizer._validate_summary_safety(unsafe_summary)

        assert result["is_safe"] is False
        assert len(result["warnings"]) > 0

    def test_parse_summary(self):
        """요약 파싱 테스트"""
        raw_summary = """
제목: CKD 환자의 혈압 관리
저자: 홍길동
연도: 2024
요약: 이 연구는 CKD 환자의 혈압 관리에 대해 다룹니다. 목표 혈압은 130/80 mmHg 이하로 권장됩니다.
주요 발견사항:
- 혈압 조절이 중요함
- 약물 치료 필요
- 정기적인 모니터링 권장
관련성: CKD 환자의 혈압 관리는 질병 진행을 늦추는 데 중요합니다.
"""

        parsed = document_summarizer._parse_summary(raw_summary)

        assert parsed["title"] == "CKD 환자의 혈압 관리"
        assert parsed["authors"] == "홍길동"
        assert parsed["year"] == "2024"
        assert "혈압 관리" in parsed["summary"]
        assert len(parsed["key_findings"]) == 3
        assert "질병 진행" in parsed["relevance"]

    @pytest.mark.asyncio
    async def test_summarize_single_document(self):
        """단일 문서 요약 테스트"""
        document = {
            "title": "CKD 환자의 식단 관리",
            "document": "CKD 환자는 저칼륨, 저나트륨, 저단백 식단을 유지해야 합니다. 이는 질병 진행을 늦추는 데 도움이 됩니다.",
            "metadata": {
                "authors": "김철수",
                "year": "2024",
                "source": "대한신장학회지",
                "doi": "10.1234/test"
            }
        }

        result = await document_summarizer.summarize(document)

        # 기본 구조 검증
        assert "title" in result
        assert "summary" in result
        assert "key_findings" in result
        assert "safety_check" in result
        assert "source" in result

        # 안전성 검증 구조 확인
        assert "is_safe" in result["safety_check"]
        assert "warnings" in result["safety_check"]

        # 출처 정보 확인
        assert "doi" in result["source"]

    @pytest.mark.asyncio
    async def test_summarize_with_stage_customization(self):
        """병기별 맞춤 요약 테스트"""
        document = {
            "title": "테스트 문서",
            "document": "테스트 내용입니다.",
            "metadata": {}
        }

        result = await document_summarizer.summarize(document, stage="3")

        assert result["stage_customized"] is True

    @pytest.mark.asyncio
    async def test_batch_summarize_multiple_documents(self):
        """배치 문서 요약 테스트"""
        documents = [
            {
                "title": "문서 1: CKD와 혈압",
                "document": "CKD 환자의 혈압 관리는 매우 중요합니다.",
                "metadata": {"authors": "저자1", "year": "2024"}
            },
            {
                "title": "문서 2: CKD와 식단",
                "document": "저칼륨 식단이 권장됩니다.",
                "metadata": {"authors": "저자2", "year": "2023"}
            }
        ]

        results = await document_summarizer.batch_summarize(documents)

        assert len(results) == 2
        assert all("title" in r for r in results)
        assert all("summary" in r for r in results)

    @pytest.mark.asyncio
    async def test_batch_summarize_max_documents(self):
        """최대 문서 개수 제한 테스트"""
        # 6개 문서 생성 (최대 5개로 제한되어야 함)
        documents = [
            {
                "title": f"문서 {i}",
                "document": f"내용 {i}",
                "metadata": {}
            }
            for i in range(6)
        ]

        results = await document_summarizer.batch_summarize(documents)

        # 최대 5개만 처리되어야 함
        assert len(results) <= 5

    @pytest.mark.asyncio
    async def test_batch_summarize_with_stage(self):
        """배치 요약 + 병기별 맞춤 테스트"""
        documents = [
            {
                "title": "문서 1",
                "document": "내용 1",
                "metadata": {}
            }
        ]

        results = await document_summarizer.batch_summarize(documents, stage="2")

        assert len(results) == 1
        assert results[0]["stage_customized"] is True

    def test_parse_summary_missing_fields(self):
        """누락된 필드가 있는 요약 파싱 테스트"""
        incomplete_summary = """
제목: 테스트
요약: 테스트 내용
"""

        parsed = document_summarizer._parse_summary(incomplete_summary)

        # 누락된 필드는 기본값 또는 빈 값으로 처리
        assert parsed["title"] == "테스트"
        assert "authors" in parsed
        assert "year" in parsed
        assert "key_findings" in parsed
        assert isinstance(parsed["key_findings"], list)

    def test_parse_summary_malformed(self):
        """잘못된 형식의 요약 파싱 테스트"""
        malformed_summary = "잘못된 형식의 요약입니다."

        parsed = document_summarizer._parse_summary(malformed_summary)

        # 파싱 실패 시에도 기본 구조 반환
        assert "title" in parsed
        assert "summary" in parsed

    @pytest.mark.asyncio
    async def test_summarize_error_handling(self):
        """요약 생성 오류 처리 테스트"""
        # 빈 문서로 오류 유도
        invalid_document = {
            "title": "",
            "document": "",
            "metadata": {}
        }

        result = await document_summarizer.summarize(invalid_document)

        # 오류가 발생해도 기본 구조는 반환되어야 함
        assert "title" in result
        assert "summary" in result
        assert "safety_check" in result

    def test_safety_check_multiple_warnings(self):
        """복수 경고 메시지 검증 테스트"""
        unsafe_summary = """
당신은 CKD 3기 병으로 진단받으세요.
이 약을 복용하세요.
괜찮습니다.
"""

        result = document_summarizer._validate_summary_safety(unsafe_summary)

        assert result["is_safe"] is False
        # 여러 경고가 감지되어야 함
        assert len(result["warnings"]) >= 2


class TestSummaryFormatting:
    """요약 형식 테스트"""

    def test_summary_structure(self):
        """요약 구조 검증"""
        raw_summary = """
제목: 테스트 문서
저자: 테스트 저자
연도: 2024
요약: 테스트 요약입니다. 이것은 두 번째 문장입니다.
주요 발견사항:
- 발견사항 1
- 발견사항 2
관련성: CKD 환자에게 중요합니다.
"""

        parsed = document_summarizer._parse_summary(raw_summary)

        # 모든 필수 필드가 존재해야 함
        required_fields = ["title", "authors", "year", "summary", "key_findings", "relevance"]
        for field in required_fields:
            assert field in parsed

    def test_key_findings_parsing(self):
        """주요 발견사항 파싱 테스트"""
        raw_summary = """
제목: 테스트
주요 발견사항:
- 첫 번째 발견사항
- 두 번째 발견사항
- 세 번째 발견사항
관련성: 테스트
"""

        parsed = document_summarizer._parse_summary(raw_summary)

        assert len(parsed["key_findings"]) == 3
        assert "첫 번째 발견사항" in parsed["key_findings"]
        assert "두 번째 발견사항" in parsed["key_findings"]

    def test_key_findings_empty(self):
        """주요 발견사항이 없는 경우 테스트"""
        raw_summary = """
제목: 테스트
요약: 테스트 요약
관련성: 테스트
"""

        parsed = document_summarizer._parse_summary(raw_summary)

        assert "key_findings" in parsed
        assert isinstance(parsed["key_findings"], list)
        assert len(parsed["key_findings"]) == 0
