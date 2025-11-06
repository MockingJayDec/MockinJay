"""
Redis 캐싱 서비스
RAG 검색 결과 및 의도 분류 결과 캐싱
"""

import logging
import json
import hashlib
from typing import Any, Optional
from redis import Redis
from redis.exceptions import RedisError
from backend.core.config import settings

logger = logging.getLogger(__name__)


class CacheService:
    """
    Redis 캐싱 서비스
    - RAG 검색 결과 캐싱
    - 의도 분류 결과 캐싱
    - TTL 기반 자동 만료
    """

    def __init__(self):
        """Redis 클라이언트 초기화"""
        try:
            self.redis_client = Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 연결 테스트
            self.redis_client.ping()
            self.enabled = True
            logger.info(f"Redis cache initialized at {settings.REDIS_HOST}:{settings.REDIS_PORT}")

        except RedisError as e:
            logger.warning(f"Redis connection failed, caching disabled: {e}")
            self.redis_client = None
            self.enabled = False

    def _generate_key(self, prefix: str, data: str) -> str:
        """
        캐시 키 생성 (해시 기반)

        Args:
            prefix: 키 접두사 (intent, rag 등)
            data: 해시할 데이터

        Returns:
            생성된 캐시 키
        """
        # 데이터를 해시하여 고정 길이 키 생성
        hash_value = hashlib.sha256(data.encode()).hexdigest()[:16]
        return f"{prefix}:{hash_value}"

    def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 데이터 가져오기

        Args:
            key: 캐시 키

        Returns:
            캐시된 데이터 또는 None
        """
        if not self.enabled:
            return None

        try:
            data = self.redis_client.get(key)
            if data:
                logger.debug(f"Cache hit: {key}")
                return json.loads(data)

            logger.debug(f"Cache miss: {key}")
            return None

        except RedisError as e:
            logger.error(f"Redis get error: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """
        캐시에 데이터 저장

        Args:
            key: 캐시 키
            value: 저장할 데이터
            ttl: Time-To-Live (초 단위, 기본값: 1시간)

        Returns:
            성공 여부
        """
        if not self.enabled:
            return False

        try:
            data = json.dumps(value, ensure_ascii=False)
            self.redis_client.setex(key, ttl, data)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True

        except RedisError as e:
            logger.error(f"Redis set error: {e}")
            return False
        except (TypeError, ValueError) as e:
            logger.error(f"JSON encode error: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        캐시 삭제

        Args:
            key: 캐시 키

        Returns:
            성공 여부
        """
        if not self.enabled:
            return False

        try:
            self.redis_client.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True

        except RedisError as e:
            logger.error(f"Redis delete error: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        패턴 매칭으로 캐시 삭제

        Args:
            pattern: 키 패턴 (예: "intent:*", "rag:*")

        Returns:
            삭제된 키 개수
        """
        if not self.enabled:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries matching pattern: {pattern}")
                return deleted
            return 0

        except RedisError as e:
            logger.error(f"Redis clear pattern error: {e}")
            return 0

    def get_intent_cache(self, question: str) -> Optional[dict]:
        """
        의도 분류 결과 캐시 조회

        Args:
            question: 사용자 질문

        Returns:
            캐시된 의도 분류 결과 또는 None
        """
        key = self._generate_key("intent", question)
        return self.get(key)

    def set_intent_cache(
        self,
        question: str,
        result: dict,
        ttl: int = 3600
    ) -> bool:
        """
        의도 분류 결과 캐시 저장

        Args:
            question: 사용자 질문
            result: 의도 분류 결과
            ttl: Time-To-Live (초 단위, 기본값: 1시간)

        Returns:
            성공 여부
        """
        key = self._generate_key("intent", question)
        return self.set(key, result, ttl)

    def get_rag_cache(
        self,
        query: str,
        intent: str,
        top_k: int = 5
    ) -> Optional[dict]:
        """
        RAG 검색 결과 캐시 조회

        Args:
            query: 검색 쿼리
            intent: 의도 타입
            top_k: 결과 개수

        Returns:
            캐시된 RAG 검색 결과 또는 None
        """
        cache_key_data = f"{query}|{intent}|{top_k}"
        key = self._generate_key("rag", cache_key_data)
        return self.get(key)

    def set_rag_cache(
        self,
        query: str,
        intent: str,
        top_k: int,
        result: dict,
        ttl: int = 86400
    ) -> bool:
        """
        RAG 검색 결과 캐시 저장

        Args:
            query: 검색 쿼리
            intent: 의도 타입
            top_k: 결과 개수
            result: RAG 검색 결과
            ttl: Time-To-Live (초 단위, 기본값: 24시간)

        Returns:
            성공 여부
        """
        cache_key_data = f"{query}|{intent}|{top_k}"
        key = self._generate_key("rag", cache_key_data)
        return self.set(key, result, ttl)

    def get_stats(self) -> dict:
        """
        캐시 통계 조회

        Returns:
            캐시 통계 정보
        """
        if not self.enabled:
            return {
                "enabled": False,
                "total_keys": 0,
                "memory_used": "0B"
            }

        try:
            info = self.redis_client.info()
            dbsize = self.redis_client.dbsize()

            return {
                "enabled": True,
                "total_keys": dbsize,
                "memory_used": info.get("used_memory_human", "Unknown"),
                "uptime_days": info.get("uptime_in_days", 0)
            }

        except RedisError as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"enabled": False, "error": str(e)}


# 싱글톤 인스턴스
cache_service = CacheService()
