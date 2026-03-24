"""헬로 라우터 예제"""
from fastapi import APIRouter
from starlette.responses import HTMLResponse

router = APIRouter(prefix="", tags=["hello"])


@router.get("/", description="인사말 반환", response_description="Hello World")
async def hello():
    """기본 인사말 엔드포인트"""
    return {"message": "Hello, World!"}


@router.get("/html", description="HTML 인사말 반환", response_class=HTMLResponse)
async def hello_html():
    """HTML 형태의 인사말 엔드포인트"""
    return "<h1>Hello, World!</h1><p>이것은 HTML 응답입니다.</p>"


@router.get("/{name}", description="이름별 인사말", response_description="이름별 인사말")
async def hello_name(name: str):
    """이름을 받아 인사말을 반환하는 엔드포인트"""
    return {"message": f"Hello, {name}!"}