from inspect import getmembers

from fastapi import FastAPI, APIRouter
from app.core.utils.api import TypedAPIRouter


def init(app: FastAPI):
    """
    Init routers and etc.
    :return:
    """
    init_routers(app)
    init_celery(app)
    init_prisma(app)


def init_routers(app: FastAPI):
    """
    Initialize routers defined in `app.api`
    :param app:
    :return:
    """
    from app.core import routers

    routers_list = [o[1] for o in getmembers(routers) if isinstance(o[1], TypedAPIRouter)]

    for router in routers_list:
        app.include_router(
            router.router,
            prefix=router.prefix,
            tags=router.tags,
            responses=router.responses
        )


def init_prisma(app: FastAPI):
    @app.on_event("startup")
    async def startup():
        from app.core.database.prisma import prisma
        await prisma.connect()

    @app.on_event("shutdown")
    async def shutdown():
        from app.core.database.prisma import prisma
        await prisma.disconnect()


def init_celery(app: FastAPI):
    print("init_celery")
