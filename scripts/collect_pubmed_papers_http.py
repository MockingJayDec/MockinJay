"""
PubMed API를 HTTP 요청으로 사용하여 CKD 관련 논문 100개 수집
"""

import sys
import json
import time
from pathlib import Path
import requests
import logging
from xml.etree import ElementTree as ET

# 프로젝트 루트 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# PubMed API 엔드포인트
PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def search_pubmed(query: str, max_results: int = 100) -> list:
    """PubMed에서 논문 ID 검색"""
    try:
        logger.info(f"PubMed 검색 시작: '{query}'")

        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": "relevance"
        }

        response = requests.get(PUBMED_SEARCH_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        id_list = data.get("esearchresult", {}).get("idlist", [])

        logger.info(f"✓ {len(id_list)}개의 논문 ID 검색 완료")
        return id_list

    except Exception as e:
        logger.error(f"PubMed 검색 오류: {e}")
        return []


def fetch_paper_details(id_list: list) -> list:
    """논문 상세 정보 가져오기"""
    papers = []

    try:
        # 배치 처리
        batch_size = 20
        for i in range(0, len(id_list), batch_size):
            batch_ids = id_list[i:i + batch_size]
            logger.info(f"논문 상세 정보 가져오는 중... ({i+1}-{i+len(batch_ids)}/{len(id_list)})")

            params = {
                "db": "pubmed",
                "id": ",".join(batch_ids),
                "retmode": "xml"
            }

            response = requests.get(PUBMED_FETCH_URL, params=params, timeout=30)
            response.raise_for_status()

            # XML 파싱
            root = ET.fromstring(response.content)

            for article in root.findall(".//PubmedArticle"):
                try:
                    pmid_elem = article.find(".//PMID")
                    pmid = pmid_elem.text if pmid_elem is not None else "Unknown"

                    # 제목
                    title_elem = article.find(".//ArticleTitle")
                    title = title_elem.text if title_elem is not None else "No title"

                    # 저자
                    authors = []
                    for author in article.findall(".//Author")[:3]:
                        lastname = author.find("LastName")
                        initials = author.find("Initials")
                        if lastname is not None and initials is not None:
                            authors.append(f"{lastname.text} {initials.text}")

                    authors_str = ", ".join(authors) if authors else "Unknown"
                    if len(article.findall(".//Author")) > 3:
                        authors_str += " et al."

                    # 초록
                    abstract_parts = []
                    for abstract_text in article.findall(".//AbstractText"):
                        if abstract_text.text:
                            abstract_parts.append(abstract_text.text)

                    abstract = " ".join(abstract_parts)[:1000] if abstract_parts else "No abstract available"

                    # 출판 연도
                    year_elem = article.find(".//PubDate/Year")
                    year = year_elem.text if year_elem is not None else "Unknown"

                    # 저널
                    journal_elem = article.find(".//Journal/Title")
                    journal = journal_elem.text if journal_elem is not None else "Unknown Journal"

                    # DOI
                    doi = "N/A"
                    for eloc in article.findall(".//ELocationID"):
                        if eloc.get("EIdType") == "doi":
                            doi = eloc.text
                            break

                    paper_data = {
                        "id": f"paper_{pmid}",
                        "pmid": pmid,
                        "title": title,
                        "authors": authors_str,
                        "year": year,
                        "journal": journal,
                        "abstract": abstract,
                        "doi": doi,
                        "keywords": ["CKD", "chronic kidney disease", "renal disease"]
                    }

                    papers.append(paper_data)

                except Exception as e:
                    logger.warning(f"논문 파싱 오류: {e}")
                    continue

            # API rate limit 준수
            time.sleep(0.5)

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
