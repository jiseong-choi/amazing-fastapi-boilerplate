from inspect import getmembers
from fastapi import FastAPI
from app.core.utils.api import TypedAPIRouter
from loguru import logger  # Loguru 라이브러리를 가져옵니다.


def init(app: FastAPI):
    init_routers(app)
    init_celery(app)
    # init_prisma(app)


def init_routers(app: FastAPI):
    try:
        from app.core import routers

        routers_list = [o[1] for o in getmembers(routers) if isinstance(o[1], TypedAPIRouter)]

        for router in routers_list:
            app.include_router(
                router.router,
                prefix=router.prefix,
                tags=router.tags,
                responses=router.responses
            )
    except Exception as e:
        # 에러 발생 시 에러 로그 추가
        logger.error(f"라우터 초기화중 에러가 발생하였습니다: {e}")
    # 라우터 초기화 로그 추가
    logger.success("라우터가 정상적으로 초기화되었습니다.")


def init_prisma(app: FastAPI):
    @app.on_event("startup")
    async def startup():
        from app.core.database.prisma import prisma
        try:
            await prisma.connect()
            # Prisma 초기화 로그 추가
            logger.success("프리즈마가 정상적으로 초기화되었습니다.")
        except Exception as e:
            # 에러 발생 시 에러 로그 추가
            logger.error(f"프리즈마 초기화중 에러가 발생하였습니다: {e}")

    @app.on_event("shutdown")
    async def shutdown():
        from app.core.database.prisma import prisma
        await prisma.disconnect()
        # Prisma 종료 로그 추가
        logger.success("프리즈마가 종료됩니다.")


def init_celery(app: FastAPI):
    try:
        # Celery 초기화 코드
        logger.success("셀러리가 정상적으로 초기화 되었습니다.")
    except Exception as e:
        # 에러 발생 시 에러 로그 추가
        logger.error(f"셀러리 초기화중 에러가 발생 하였습니다: {e}")
