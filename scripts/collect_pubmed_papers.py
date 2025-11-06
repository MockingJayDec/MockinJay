"""
PubMed API를 사용하여 CKD 관련 논문 100개 수집
"""

import sys
import json
import time
from pathlib import Path
from Bio import Entrez
import logging

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PubMed API 설정 (이메일 필수)
Entrez.email = "your.email@example.com"  # 실제 프로젝트에서는 환경 변수로 관리


def search_pubmed(query: str, max_results: int = 100) -> list:
    """PubMed에서 논문 ID 검색"""
    try:
        logger.info(f"PubMed 검색 시작: '{query}'")
        handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort="relevance"
        )
        record = Entrez.read(handle)
        handle.close()

        id_list = record["IdList"]
        logger.info(f"✓ {len(id_list)}개의 논문 ID 검색 완료")
        return id_list

    except Exception as e:
        logger.error(f"PubMed 검색 오류: {e}")
        return []


def fetch_paper_details(id_list: list) -> list:
    """논문 상세 정보 가져오기"""
    papers = []

    try:
        # PubMed API는 한 번에 최대 200개까지 가능
        batch_size = 100
        for i in range(0, len(id_list), batch_size):
            batch_ids = id_list[i:i + batch_size]
            logger.info(f"논문 상세 정보 가져오는 중... ({i+1}-{i+len(batch_ids)}/{len(id_list)})")

            # 논문 상세 정보 가져오기
            handle = Entrez.efetch(
                db="pubmed",
                id=batch_ids,
                rettype="medline",
                retmode="text"
            )

            records = Entrez.read(handle)
            handle.close()

            # 각 논문 정보 파싱
            for record in records['PubmedArticle']:
                try:
                    article = record['MedlineCitation']['Article']
                    pmid = str(record['MedlineCitation']['PMID'])

                    # 제목
                    title = article.get('ArticleTitle', 'No title')

                    # 저자
                    authors = []
                    if 'AuthorList' in article:
                        for author in article['AuthorList'][:3]:  # 최대 3명
                            if 'LastName' in author and 'Initials' in author:
                                authors.append(f"{author['LastName']} {author['Initials']}")
                    authors_str = ", ".join(authors) if authors else "Unknown"
                    if len(article.get('AuthorList', [])) > 3:
                        authors_str += " et al."

                    # 초록
                    abstract = ""
                    if 'Abstract' in article and 'AbstractText' in article['Abstract']:
                        abstract_parts = article['Abstract']['AbstractText']
                        if isinstance(abstract_parts, list):
                            abstract = " ".join([str(part) for part in abstract_parts])
                        else:
                            abstract = str(abstract_parts)

                    # 출판 연도
                    year = "Unknown"
                    if 'Journal' in article and 'JournalIssue' in article['Journal']:
                        pub_date = article['Journal']['JournalIssue'].get('PubDate', {})
                        year = pub_date.get('Year', 'Unknown')

                    # 저널
                    journal = article.get('Journal', {}).get('Title', 'Unknown Journal')

                    # DOI
                    doi = "N/A"
                    if 'ELocationID' in article:
                        for eloc in article['ELocationID']:
                            if eloc.attributes.get('EIdType') == 'doi':
                                doi = str(eloc)
                                break

                    paper_data = {
                        "id": f"paper_{pmid}",
                        "pmid": pmid,
                        "title": title,
                        "authors": authors_str,
                        "year": year,
                        "journal": journal,
                        "abstract": abstract[:1000] if abstract else "No abstract available",  # 초록 길이 제한
                        "doi": doi,
                        "keywords": ["CKD", "chronic kidney disease", "renal disease"]
                    }

                    papers.append(paper_data)

                except Exception as e:
                    logger.warning(f"논문 파싱 오류 (PMID: {pmid}): {e}")
                    continue

            # API rate limit 준수 (최대 3 requests/second)
            time.sleep(0.4)

        logger.info(f"✓ {len(papers)}개의 논문 상세 정보 수집 완료")
        return papers

    except Exception as e:
        logger.error(f"논문 상세 정보 가져오기 오류: {e}")
        return papers


def save_papers_to_json(papers: list, output_file: Path):
    """논문 데이터를 JSON 파일로 저장"""
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(papers, f, ensure_ascii=False, indent=2)
        logger.info(f"✓ 논문 데이터 저장 완료: {output_file}")
        return True
    except Exception as e:
        logger.error(f"파일 저장 오류: {e}")
        return False


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("PubMed CKD 논문 수집 시작")
    logger.info("=" * 60)

    # 검색 쿼리 (CKD 관련)
    search_query = "chronic kidney disease[Title/Abstract] AND (management OR treatment OR therapy)"

    # 논문 ID 검색
    paper_ids = search_pubmed(search_query, max_results=100)

    if paper_ids:
        # 논문 상세 정보 가져오기
        papers = fetch_paper_details(paper_ids)

        if papers:
            # JSON 파일로 저장
            output_file = project_root / "data" / "raw" / "ckd_papers_100.json"
            save_papers_to_json(papers, output_file)

            logger.info("\n" + "=" * 60)
            logger.info(f"✅ 총 {len(papers)}개의 논문 수집 완료!")
            logger.info("=" * 60)
        else:
            logger.error("논문 상세 정보를 가져오지 못했습니다.")
    else:
        logger.error("논문 검색 결과가 없습니다.")
