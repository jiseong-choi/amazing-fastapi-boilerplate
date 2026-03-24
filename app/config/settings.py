"""통합 설정 관리"""
from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, validator
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class Settings(BaseSettings):
    """애플리케이션 통합 설정"""
    
    # API 기본 설정
    API_NAME: str = "HumanBeing"
    API_VERSION: str = "0.0.1 beta"
    API_DESCRIPTION: str = "HumanBeing API"
    DEBUG: bool = False
    TESTING: bool = False
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # CORS 설정
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # 데이터베이스 설정 (Prisma)
    DATABASE_URL: str = "mysql://root:root@localhost:3306/base"
    
    # Celery 설정
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # 보안 설정 (나중에 사용)
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # API 키 설정 (AI 에이전트 인증)
    API_KEYS: List[str] = ["test_key"]  # 실제 운영에서는 환경 변수로 관리
    REQUIRE_API_KEY: bool = False  # 개발 환경에서는 False
    
    # Pydantic v2 설정
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    @property
    def is_testing(self) -> bool:
        """테스트 환경 여부"""
        return self.TESTING or os.environ.get("API_TEST") == "1"


# 싱글턴 인스턴스
settings = Settings()