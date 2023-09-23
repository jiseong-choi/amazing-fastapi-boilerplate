from app.core.routers.hello import router as hello_router
from app.core.utils.api import TypedAPIRouter

hello_router = TypedAPIRouter(router=hello_router, prefix="/hello", tags=["hello"])