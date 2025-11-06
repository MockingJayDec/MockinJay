"""
PubMed API Client
RESEARCH 의도를 위한 논문 검색 클라이언트
"""

import logging
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import urlencode
import time

logger = logging.getLogger(__name__)


class PubMedClient:
    """
    PubMed E-utilities API 클라이언트
    https://www.ncbi.nlm.nih.gov/books/NBK25501/
    """

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    ESEARCH_URL = f"{BASE_URL}/esearch.fcgi"
    EFETCH_URL = f"{BASE_URL}/efetch.fcgi"
    ESUMMARY_URL = f"{BASE_URL}/esummary.fcgi"

    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        """
        PubMed API 클라이언트 초기화

        Args:
            email: NCBI 가이드라인에 따른 이메일 (선택사항)
            api_key: API 키 (선택사항, 요청 속도 제한 완화)
        """
        self.email = email
        self.api_key = api_key
        self.rate_limit_delay = 0.34 if not api_key else 0.1  # API 키 없으면 3req/s, 있으면 10req/s
        self.last_request_time = 0

        logger.info("PubMed API Client initialized")

    def search(
        self,
        query: str,
        max_results: int = 5,
        sort: str = "relevance",
        filters: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        PubMed 논문 검색

        Args:
            query: 검색 쿼리
            max_results: 최대 결과 개수
            sort: 정렬 방식 (relevance, pub_date)
            filters: 추가 필터 (예: {"mindate": "2020", "maxdate": "2024"})

        Returns:
            논문 정보 리스트
        """
        try:
            # 1. ESearch: 논문 ID 검색
            pmids = self._esearch(query=query, max_results=max_results, sort=sort, filters=filters)

            if not pmids:
                logger.info(f"No results found for query: {query}")
                return []

            # 2. ESummary: 논문 요약 정보 가져오기
            summaries = self._esummary(pmids=pmids)

            # 3. 결과 포맷팅
            formatted_results = self._format_results(summaries)

            logger.info(f"Found {len(formatted_results)} PubMed results for query: {query}")
            return formatted_results

        except Exception as e:
            logger.error(f"PubMed search failed: {e}")
            return []

    def _esearch(
        self,
        query: str,
        max_results: int = 5,
        sort: str = "relevance",
        filters: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """
        ESearch API 호출 - 논문 ID 검색

        Args:
            query: 검색 쿼리
            max_results: 최대 결과 개수
            sort: 정렬 방식
            filters: 추가 필터

        Returns:
            PubMed ID 리스트
        """
        try:
            # Rate limiting
            self._wait_for_rate_limit()

            # API 파라미터 구성
            params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": sort
            }

            # 이메일 추가 (NCBI 가이드라인)
            if self.email:
                params["email"] = self.email

            # API 키 추가
            if self.api_key:
                params["api_key"] = self.api_key

            # 필터 추가
            if filters:
                params.update(filters)

            # API 요청
            response = requests.get(self.ESEARCH_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # PMID 추출
            pmids = data.get("esearchresult", {}).get("idlist", [])

            return pmids

        except requests.RequestException as e:
            logger.error(f"ESearch API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"ESearch failed: {e}")
            return []

    def _esummary(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """
        ESummary API 호출 - 논문 요약 정보 가져오기

        Args:
            pmids: PubMed ID 리스트

        Returns:
            논문 요약 정보 리스트
        """
        try:
            # Rate limiting
            self._wait_for_rate_limit()

            # API 파라미터 구성
            params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "json"
            }

            # 이메일 추가
            if self.email:
                params["email"] = self.email

            # API 키 추가
            if self.api_key:
                params["api_key"] = self.api_key

            # API 요청
            response = requests.get(self.ESUMMARY_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            # 결과 추출
            result = data.get("result", {})
            summaries = []

            for pmid in pmids:
                if pmid in result:
                    summaries.append(result[pmid])

            return summaries

        except requests.RequestException as e:
            logger.error(f"ESummary API request failed: {e}")
            return []
        except Exception as e:
            logger.error(f"ESummary failed: {e}")
            return []

    def _format_results(self, summaries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        PubMed 검색 결과 포맷팅

        Args:
            summaries: ESummary 응답 데이터

        Returns:
            포맷팅된 논문 정보 리스트
        """
        formatted = []

        for summary in summaries:
            try:
                # 저자 리스트 구성
                authors = []
                for author in summary.get("authors", []):
                    author_name = author.get("name", "")
                    if author_name:
                        authors.append(author_name)

                # 결과 딕셔너리 구성
                formatted_result = {
                    "id": f"PMID:{summary.get('uid', '')}",
                    "document": summary.get("title", ""),
                    "metadata": {
                        "pmid": summary.get("uid", ""),
                        "title": summary.get("title", ""),
                        "authors": authors,
                        "source": summary.get("source", ""),
                        "pub_date": summary.get("pubdate", ""),
                        "pub_type": summary.get("pubtype", []),
                        "doi": summary.get("elocationid", ""),
                        "journal": summary.get("fulljournalname", ""),
                    },
                    "source": "pubmed",
                    "intent": "RESEARCH",
                    "similarity_score": 0.0  # PubMed API는 유사도 점수를 제공하지 않음
                }

                formatted.append(formatted_result)

            except Exception as e:
                logger.error(f"Failed to format PubMed result: {e}")
                continue

        return formatted

    def _wait_for_rate_limit(self):
        """Rate limiting을 위한 대기"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last_request)

        self.last_request_time = time.time()

    def get_article_abstract(self, pmid: str) -> Optional[str]:
        """
        논문 초록 가져오기 (EFetch API 사용)

        Args:
            pmid: PubMed ID

        Returns:
            논문 초록 텍스트
        """
        try:
            # Rate limiting
            self._wait_for_rate_limit()

            # API 파라미터 구성
            params = {
                "db": "pubmed",
                "id": pmid,
                "retmode": "xml",
                "rettype": "abstract"
            }

            # 이메일 추가
            if self.email:
                params["email"] = self.email

            # API 키 추가
            if self.api_key:
                params["api_key"] = self.api_key

            # API 요청
            response = requests.get(self.EFETCH_URL, params=params, timeout=10)
            response.raise_for_status()

            # XML 파싱하여 초록 추출 (간단한 구현)
            # 실제로는 XML 파서 사용 권장
            xml_text = response.text

            # <AbstractText> 태그 내용 추출
            import re
            abstract_match = re.search(r'<AbstractText>(.*?)</AbstractText>', xml_text, re.DOTALL)

            if abstract_match:
                return abstract_match.group(1).strip()

            return None

        except Exception as e:
            logger.error(f"Failed to fetch abstract for PMID {pmid}: {e}")
            return None


# 싱글톤 인스턴스
pubmed_client = PubMedClient()
