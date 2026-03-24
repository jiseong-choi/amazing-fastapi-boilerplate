from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from loguru import logger
import sys

from app.config.settings import settings
from app.middleware import setup_middleware
from app.exceptions import (
    app_exception_handler,
    http_exception_handler,
    generic_exception_handler,
    AppException,
)
from app.routers import setup_routers

# 로그 설정
logger.remove()
logger.add(
    sys.stderr,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
)
if settings.LOG_FILE:
    logger.add(settings.LOG_FILE, rotation="10 MB", retention="30 days")

# FastAPI 앱 생성
app = FastAPI(
    title=settings.API_NAME,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    debug=settings.DEBUG,
    openapi_tags=[
        {"name": "AI Agent", "description": "AI 에이전트를 위한 API 엔드포인트"},
        {"name": "hello", "description": "기본 인사말 API"},
    ],
    servers=[
        {"url": "http://localhost:8000", "description": "개발 서버"},
        {"url": "https://api.example.com", "description": "프로덕션 서버"},
    ],
    openapi_extra={
        "x-ai-capabilities": ["text_processing", "web_search", "data_analysis"],
        "x-rate-limit": {
            "requests_per_minute": 60,
            "requests_per_day": 1000,
        },
        "x-examples": {
            "python": "import requests\nresponse = requests.get('http://localhost:8000/v1/agent/capabilities')\nprint(response.json())",
            "javascript": "fetch('http://localhost:8000/v1/agent/capabilities')\n  .then(response => response.json())\n  .then(data => console.log(data));",
        },
    },
)

# 예외 핸들러 등록
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

logger.info("프로젝트 초기화를 시작합니다.")

# 미들웨어 설정
setup_middleware(app)

# 라우터 설정
setup_routers(app)

logger.success("초기화가 완료되었습니다.")