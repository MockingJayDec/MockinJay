"""
CKD 논문 데이터를 ChromaDB에 로드하는 스크립트
"""

import json
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.vector_db import vector_db
import logging

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_paper_data_to_db():
    """100개의 CKD 논문 데이터를 ChromaDB에 로드"""

    # JSON 파일 경로
    paper_file_path = project_root / "data" / "raw" / "ckd_papers_100.json"

    if not paper_file_path.exists():
        logger.error(f"논문 데이터 파일을 찾을 수 없습니다: {paper_file_path}")
        return False

    try:
        # JSON 파일 로드
        with open(paper_file_path, "r", encoding="utf-8") as f:
            paper_data = json.load(f)

        logger.info(f"✓ {len(paper_data)}개의 논문 데이터 로드 완료")

        # 문서와 메타데이터 분리
        documents = []
        metadatas = []
        ids = []

        for paper in paper_data:
            # 논문 정보를 문서로 포맷팅
            doc_text = f"""Title: {paper['title']}
Authors: {paper['authors']}
Year: {paper['year']}
Journal: {paper['journal']}
Abstract: {paper['abstract']}
DOI: {paper['doi']}"""

            documents.append(doc_text)

            # 메타데이터 생성
            metadata = {
                "pmid": paper["pmid"],
                "year": paper["year"],
                "journal": paper["journal"],
                "doi": paper["doi"],
                "keywords": ", ".join(paper["keywords"])
            }
            metadatas.append(metadata)

            # ID 추가
            ids.append(paper["id"])

        logger.info(f"✓ 문서 {len(documents)}개 준비 완료")

        # ChromaDB에 추가
        logger.info("ChromaDB에 논문 데이터 업로드 중...")
        success = vector_db.add_documents(
            intent="RESEARCH",
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        if success:
            logger.info(f"✅ {len(documents)}개의 논문 데이터를 ChromaDB에 업로드 완료!")

            # 검증: 데이터 개수 확인
            count = vector_db.collections["RESEARCH"].count()
            logger.info(f"RESEARCH 컬렉션 총 문서 개수: {count}")

            return True
        else:
            logger.error("❌ ChromaDB 업로드 실패")
            return False

    except json.JSONDecodeError as e:
        logger.error(f"JSON 파일 파싱 오류: {e}")
        return False
    except Exception as e:
        logger.error(f"데이터 로드 중 오류 발생: {e}")
        return False


def verify_data():
    """업로드된 데이터 검증"""
    try:
        # 샘플 검색 테스트
        test_query = "chronic kidney disease management strategies"
        logger.info(f"\n검증 쿼리: '{test_query}'")

        results = vector_db.search(
            intent="RESEARCH",
            query=test_query,
            top_k=3
        )

        if results:
            logger.info(f"✅ 검색 결과 {len(results)}개 반환:")
            for i, result in enumerate(results, 1):
                logger.info(f"\n[결과 {i}]")
                logger.info(f"제목: {result['document'][:100]}...")
                logger.info(f"유사도 점수: {result['similarity_score']:.4f}")
                logger.info(f"메타데이터: {result['metadata']}")
            return True
        else:
            logger.warning("검색 결과가 없습니다.")
            return False

    except Exception as e:
        logger.error(f"데이터 검증 중 오류: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("CKD 논문 데이터 로드 시작")
    logger.info("=" * 60)

    # 데이터 로드
    success = load_paper_data_to_db()

    if success:
        # 데이터 검증
        logger.info("\n" + "=" * 60)
        logger.info("데이터 검증 시작")
        logger.info("=" * 60)
        verify_data()

    logger.info("\n" + "=" * 60)
    logger.info("프로세스 완료")
    logger.info("=" * 60)
