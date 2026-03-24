"""애플리케이션 초기화 모듈 (구버전 호환성 유지)"""
from fastapi import FastAPI
from loguru import logger


def init(app: FastAPI):
    """
    기존 호환성을 위한 초기화 함수.
    이제 대부분의 초기화는 main.py에서 직접 수행됩니다.
    """
    logger.warning("구버전 init() 함수가 호출되었습니다. main.py에서 직접 초기화를 수행합니다.")
    
    # Prisma 초기화 (주석 처리됨)
    # init_prisma(app)
    
    # Celery 초기화
    init_celery(app)


def init_prisma(app: FastAPI):
    """Prisma 데이터베이스 연결 초기화"""
    @app.on_event("startup")
    async def startup():
        try:
            from app.core.database.prisma import prisma
            await prisma.connect()
            logger.success("Prisma가 정상적으로 초기화되었습니다.")
        except ImportError:
            logger.warning("Prisma를 사용할 수 없습니다.")
        except Exception as e:
            logger.error(f"Prisma 초기화 중 오류 발생: {e}")

    @app.on_event("shutdown")
    async def shutdown():
        try:
            from app.core.database.prisma import prisma
            await prisma.disconnect()
            logger.info("Prisma 연결이 종료되었습니다.")
        except Exception as e:
            logger.error(f"Prisma 종료 중 오류 발생: {e}")


def init_celery(app: FastAPI):
    """Celery 작업 큐 초기화"""
    try:
        # Celery 초기화 코드 (나중에 구현)
        logger.info("Celery 초기화가 필요합니다.")
    except Exception as e:
        logger.error(f"Celery 초기화 중 오류 발생: {e}")
