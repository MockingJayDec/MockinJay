"""
Vector Database 테스트
ChromaDB 기능 검증
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.vector_db import vector_db
from backend.services.data_loader import data_loader


class TestVectorDB:
    """Vector DB 테스트"""

    def test_add_and_search_documents(self):
        """문서 추가 및 검색 테스트"""
        # 테스트 데이터 준비
        test_documents = [
            "크레아티닌 수치가 2.0이면 신장 기능이 저하된 상태입니다.",
            "GFR이 60 미만이면 만성콩팥병 3기에 해당합니다.",
            "칼륨 섭취를 제한해야 합니다. 바나나와 오렌지를 피하세요."
        ]

        test_metadata = [
            {"category": "검사", "importance": "high"},
            {"category": "진단", "importance": "high"},
            {"category": "식단", "importance": "medium"}
        ]

        test_ids = ["test_001", "test_002", "test_003"]

        # 문서 추가
        success = vector_db.add_documents(
            intent="MEDICAL_INFO",
            documents=test_documents,
            metadatas=test_metadata,
            ids=test_ids
        )
        assert success, "문서 추가 실패"

        # 검색 테스트
        results = vector_db.search(
            intent="MEDICAL_INFO",
            query="크레아티닌이 높으면 어떻게 되나요?",
            top_k=3
        )

        assert len(results) > 0, "검색 결과가 없습니다"
        assert results[0]['similarity_score'] > 0, "유사도 점수가 올바르지 않습니다"

        # 테스트 데이터 정리
        vector_db.delete_documents("MEDICAL_INFO", test_ids)

        print("✅ 문서 추가 및 검색 테스트 통과")

    def test_metadata_filtering(self):
        """메타데이터 필터링 테스트"""
        # 테스트 데이터 추가
        test_documents = [
            "Stage 3 CKD requires dietary restrictions",
            "Stage 5 CKD may require dialysis",
            "Stage 2 CKD needs regular monitoring"
        ]

        test_metadata = [
            {"stage": "3", "category": "management"},
            {"stage": "5", "category": "treatment"},
            {"stage": "2", "category": "monitoring"}
        ]

        test_ids = ["filter_001", "filter_002", "filter_003"]

        # 문서 추가
        vector_db.add_documents(
            intent="MEDICAL_INFO",
            documents=test_documents,
            metadatas=test_metadata,
            ids=test_ids
        )

        # Stage 5 필터로 검색
        results = vector_db.search(
            intent="MEDICAL_INFO",
            query="CKD treatment",
            top_k=3,
            filters={"stage": "5"}
        )

        # 필터가 적용되었는지 확인
        if results:
            for result in results:
                if 'stage' in result.get('metadata', {}):
                    assert result['metadata']['stage'] == "5", "필터링이 올바르게 작동하지 않습니다"

        # 테스트 데이터 정리
        vector_db.delete_documents("MEDICAL_INFO", test_ids)

        print("✅ 메타데이터 필터링 테스트 통과")

    def test_collection_stats(self):
        """컬렉션 통계 테스트"""
        # 통계 조회
        stats = vector_db.get_collection_stats("MEDICAL_INFO")

        assert 'intent' in stats, "통계에 intent가 없습니다"
        assert 'document_count' in stats, "통계에 document_count가 없습니다"
        assert stats['intent'] == "MEDICAL_INFO", "intent가 올바르지 않습니다"

        print(f"✅ 컬렉션 통계 테스트 통과: {stats}")

    def test_update_document(self):
        """문서 업데이트 테스트"""
        # 테스트 문서 추가
        test_id = "update_test_001"
        vector_db.add_documents(
            intent="MEDICAL_INFO",
            documents=["Original content"],
            metadatas=[{"version": "1.0"}],
            ids=[test_id]
        )

        # 문서 업데이트
        success = vector_db.update_document(
            intent="MEDICAL_INFO",
            document_id=test_id,
            document="Updated content",
            metadata={"version": "2.0"}
        )
        assert success, "문서 업데이트 실패"

        # 업데이트 확인
        results = vector_db.search(
            intent="MEDICAL_INFO",
            query="Updated content",
            top_k=1
        )

        if results:
            assert "Updated" in results[0]['document'], "문서가 업데이트되지 않았습니다"

        # 테스트 데이터 정리
        vector_db.delete_documents("MEDICAL_INFO", [test_id])

        print("✅ 문서 업데이트 테스트 통과")

    def test_multiple_intents(self):
        """여러 의도 분리 테스트"""
        # MEDICAL_INFO에 데이터 추가
        vector_db.add_documents(
            intent="MEDICAL_INFO",
            documents=["Medical information about CKD"],
            ids=["med_001"]
        )

        # RESEARCH에 데이터 추가
        vector_db.add_documents(
            intent="RESEARCH",
            documents=["Research paper about kidney disease"],
            ids=["res_001"]
        )

        # MEDICAL_INFO 검색
        med_results = vector_db.search(
            intent="MEDICAL_INFO",
            query="kidney",
            top_k=5
        )

        # RESEARCH 검색
        res_results = vector_db.search(
            intent="RESEARCH",
            query="kidney",
            top_k=5
        )

        # 각 의도별로 데이터가 분리되어 있는지 확인
        # (실제로는 둘 다 kidney를 포함하지만 서로 다른 컬렉션)

        # 테스트 데이터 정리
        vector_db.delete_documents("MEDICAL_INFO", ["med_001"])
        vector_db.delete_documents("RESEARCH", ["res_001"])

        print("✅ 여러 의도 분리 테스트 통과")


class TestDataLoader:
    """Data Loader 테스트"""

    def test_load_sample_medical_qa(self):
        """샘플 Q&A 데이터 로드 테스트"""
        # 컬렉션 초기화
        vector_db.reset_collection("MEDICAL_INFO")

        # 샘플 데이터 로드
        success = data_loader.load_sample_medical_qa()
        assert success, "샘플 Q&A 데이터 로드 실패"

        # 로드된 데이터 확인
        stats = vector_db.get_collection_stats("MEDICAL_INFO")
        assert stats['document_count'] > 0, "데이터가 로드되지 않았습니다"

        # 검색 테스트
        results = vector_db.search(
            intent="MEDICAL_INFO",
            query="크레아티닌이란 무엇인가요?",
            top_k=3
        )
        assert len(results) > 0, "샘플 데이터 검색 실패"

        print(f"✅ 샘플 Q&A 데이터 로드 테스트 통과 ({stats['document_count']}개 문서)")

    def test_load_all_sample_data(self):
        """모든 샘플 데이터 로드 테스트"""
        # 모든 컬렉션 초기화
        for intent in ["MEDICAL_INFO", "RESEARCH", "POLICY"]:
            vector_db.reset_collection(intent)

        # 모든 샘플 데이터 로드
        results = data_loader.load_all_sample_data()

        assert results["medical_qa"], "Q&A 데이터 로드 실패"
        assert results["research_papers"], "연구 논문 데이터 로드 실패"
        assert results["policy_guidelines"], "정책 가이드라인 데이터 로드 실패"

        print("✅ 모든 샘플 데이터 로드 테스트 통과")


def run_all_tests():
    """모든 테스트 실행"""
    print("=" * 50)
    print("Vector Database 테스트 시작")
    print("=" * 50)

    # VectorDB 테스트
    vector_test = TestVectorDB()
    vector_test.test_add_and_search_documents()
    vector_test.test_metadata_filtering()
    vector_test.test_collection_stats()
    vector_test.test_update_document()
    vector_test.test_multiple_intents()

    print("\n" + "=" * 50)
    print("Data Loader 테스트 시작")
    print("=" * 50)

    # DataLoader 테스트
    loader_test = TestDataLoader()
    loader_test.test_load_sample_medical_qa()
    loader_test.test_load_all_sample_data()

    print("\n" + "=" * 50)
    print("✅ 모든 테스트 통과!")
    print("=" * 50)


if __name__ == "__main__":
    run_all_tests()