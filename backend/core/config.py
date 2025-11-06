"""
환경 변수 및 설정 관리
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 프로젝트 기본 정보
    PROJECT_NAME: str = "MockinJay"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"  # development, staging, production

    # API 설정
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # LLM API 키
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""

    # Vector Database (ChromaDB - Free, Local)
    CHROMA_PERSIST_DIRECTORY: str = "data/chroma_db"
    CHROMA_COLLECTION_PREFIX: str = "mockinjay"
    # ChromaDB doesn't require API keys - runs locally!

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/mockinjay"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: str = "redis://localhost:6379/0"

    # PubMed API
    PUBMED_API_KEY: str = ""
    PUBMED_EMAIL: str = ""

    # 로깅
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    # 보안
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 파일 경로
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    MODELS_DIR: Path = BASE_DIR / "models"
    LOGS_DIR: Path = BASE_DIR / "logs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 디렉토리 생성
        self.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.MODELS_DIR.mkdir(parents=True, exist_ok=True)


# 전역 설정 인스턴스
settings = Settings()
