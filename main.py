from fastapi import FastAPI
from loguru import logger

from app.config import openapi_config
from app.initializer import init

app = FastAPI(
    title=openapi_config.name,
    version=openapi_config.version,
    description=openapi_config.description,
)

logger.info("프로젝트 초기화를 시작합니다.")
init(app)
logger.success("초기화가 완료되었습니다.")