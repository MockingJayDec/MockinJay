"""
CKD 논문 대용량 데이터(paper_dataset_enriched_s2_checkpoint_4850.jsonl)를
ChromaDB에 로드하는 스크립트

- 총 4,850개 논문 데이터
- JSONL 형식 (각 줄이 별도의 JSON 객체)
- 배치 처리 (1000개씩 청크)
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
import time

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

# 배치 크기 (한 번에 처리할 문서 개수)
BATCH_SIZE = 1000


def parse_jsonl_file(file_path: Path) -> List[Dict[str, Any]]:
    """
    JSONL 파일을 파싱하여 리스트로 반환

    Args:
        file_path: JSONL 파일 경로

    Returns:
        파싱된 논문 데이터 리스트
    """
    papers = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            try:
                paper = json.loads(line.strip())
                papers.append(paper)
            except json.JSONDecodeError as e:
                logger.warning(f"라인 {line_num} 파싱 실패: {e}")
                continue

    return papers


def prepare_documents_batch(papers: List[Dict[str, Any]]) -> tuple:
    """
    논문 데이터를 ChromaDB 형식으로 변환

    Args:
        papers: 논문 데이터 리스트

    Returns:
        (documents, metadatas, ids) 튜플
    """
    documents = []
    metadatas = []
    ids = []

    for idx, paper in enumerate(papers):
        try:
            # 필수 필드 검증
            if not paper.get('title') or not paper.get('abstract'):
                logger.warning(f"논문 {idx}: 필수 필드 누락 (title 또는 abstract)")
                continue

            # 메타데이터 추출
            metadata_obj = paper.get('metadata', {})

            # 저자 리스트를 문자열로 변환
            authors = metadata_obj.get('authors', [])
            authors_str = ', '.join(authors) if isinstance(authors, list) else str(authors)

            # 키워드 리스트를 문자열로 변환
            keywords = metadata_obj.get('keywords', [])
            keywords_str = ', '.join(keywords) if isinstance(keywords, list) else str(keywords)

            # 연도 추출 (publication_date에서)
            pub_date = metadata_obj.get('publication_date', '')
            year = pub_date.split('.')[0] if pub_date else 'Unknown'

            # 문서 텍스트 생성 (임베딩에 사용됨)
            doc_text = f"""Title: {paper['title']}
Authors: {authors_str}
Year: {year}
Journal: {metadata_obj.get('journal', 'Unknown')}
Keywords: {keywords_str}
Abstract: {paper['abstract']}
DOI: {metadata_obj.get('doi', 'N/A')}"""

            documents.append(doc_text)

            # 메타데이터 생성 (검색 시 반환됨)
            metadata = {
                "title": paper['title'],
                "authors": authors_str,
                "year": year,
                "journal": metadata_obj.get('journal', 'Unknown'),
                "doi": metadata_obj.get('doi', ''),
                "keywords": keywords_str,
                "source": metadata_obj.get('source', 'pubmed'),
                "publication_date": pub_date
            }
            metadatas.append(metadata)

            # ID 생성 (DOI 기반 또는 순차 ID)
            doi = metadata_obj.get('doi', '')
            paper_id = f"enriched_paper_{doi.replace('/', '_')}" if doi else f"enriched_paper_{idx}"
            ids.append(paper_id)

        except Exception as e:
            logger.error(f"논문 {idx} 처리 중 오류: {e}")
            continue

    return documents, metadatas, ids


def load_papers_in_batches(papers: List[Dict[str, Any]]) -> bool:
    """
    논문 데이터를 배치로 나누어 ChromaDB에 로드

    Args:
        papers: 전체 논문 데이터 리스트

    Returns:
        성공 여부
    """
    total_papers = len(papers)
    total_batches = (total_papers + BATCH_SIZE - 1) // BATCH_SIZE

    logger.info(f"총 {total_papers:,}개 논문을 {total_batches}개 배치로 나누어 로드")

    successful_count = 0

    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, total_papers)

        batch_papers = papers[start_idx:end_idx]

        logger.info(f"\n배치 {batch_num + 1}/{total_batches} 처리 중 ({start_idx+1}-{end_idx})")

        # 문서 준비
        documents, metadatas, ids = prepare_documents_batch(batch_papers)

        if not documents:
            logger.warning(f"배치 {batch_num + 1}: 유효한 문서 없음")
            continue

        logger.info(f"  → {len(documents)}개 문서 준비 완료")

        # ChromaDB에 추가
        try:
            logger.info(f"  → ChromaDB 업로드 중...")
            start_time = time.time()

            success = vector_db.add_documents(
                intent="RESEARCH",
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            elapsed = time.time() - start_time

            if success:
                successful_count += len(documents)
                logger.info(f"  ✅ 배치 업로드 완료 ({elapsed:.1f}초)")
            else:
                logger.error(f"  ❌ 배치 업로드 실패")

        except Exception as e:
            logger.error(f"  ❌ 배치 {batch_num + 1} 업로드 중 오류: {e}")
            continue

        # API 호출 제한 방지를 위한 짧은 대기
        if batch_num < total_batches - 1:
            time.sleep(1)

    logger.info(f"\n총 {successful_count:,}/{total_papers:,}개 논문 업로드 완료")

    return successful_count > 0


def verify_data():
    """업로드된 데이터 검증"""
    try:
        # ChromaDB 컬렉션 상태 확인
        count = vector_db.collections["RESEARCH"].count()
        logger.info(f"\nRESearch 컬렉션 총 문서 개수: {count:,}")

        # 샘플 검색 테스트
        test_queries = [
            "chronic kidney disease treatment efficacy",
            "SGLT2 inhibitors renal protection",
            "proteinuria progression markers"
        ]

        for query in test_queries:
            logger.info(f"\n검증 쿼리: '{query}'")

            results = vector_db.search(
                intent="RESEARCH",
                query=query,
                top_k=3
            )

            if results:
                logger.info(f"✅ 검색 결과 {len(results)}개 반환:")
                for i, result in enumerate(results, 1):
                    title = result['metadata'].get('title', 'N/A')
                    year = result['metadata'].get('year', 'N/A')
                    journal = result['metadata'].get('journal', 'N/A')
                    score = result['similarity_score']

                    logger.info(f"\n  [{i}] {title}")
                    logger.info(f"      Year: {year} | Journal: {journal}")
                    logger.info(f"      Similarity: {score:.4f}")
            else:
                logger.warning("검색 결과가 없습니다.")

        return True

    except Exception as e:
        logger.error(f"데이터 검증 중 오류: {e}")
        return False


def main():
    """메인 실행 함수"""
    logger.info("=" * 80)
    logger.info("CKD 논문 대용량 데이터 로드 시작")
    logger.info("=" * 80)

    # 파일 경로
    jsonl_file = project_root / "data" / "raw" / "paper_dataset_enriched_s2_checkpoint_4850.jsonl"

    if not jsonl_file.exists():
        logger.error(f"❌ 파일을 찾을 수 없습니다: {jsonl_file}")
        return

    try:
        # 1. JSONL 파일 파싱
        logger.info(f"\n📄 JSONL 파일 파싱 중: {jsonl_file.name}")
        papers = parse_jsonl_file(jsonl_file)
        logger.info(f"✓ {len(papers):,}개 논문 데이터 로드 완료")

        # 2. 배치 업로드
        logger.info("\n" + "=" * 80)
        logger.info("ChromaDB 배치 업로드")
        logger.info("=" * 80)
        success = load_papers_in_batches(papers)

        if not success:
            logger.error("❌ 데이터 업로드 실패")
            return

        # 3. 데이터 검증
        logger.info("\n" + "=" * 80)
        logger.info("데이터 검증")
        logger.info("=" * 80)
        verify_data()

        logger.info("\n" + "=" * 80)
        logger.info("✅ 프로세스 완료!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ 프로세스 실행 중 오류: {e}", exc_info=True)


if __name__ == "__main__":
    main()
