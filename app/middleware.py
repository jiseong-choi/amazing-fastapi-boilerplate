"""미들웨어 설정"""
import time
from typing import Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.config.settings import settings


class LoggingMiddleware(BaseHTTPMiddleware):
    """요청/응답 로깅 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 요청 시작 시간
        start_time = time.time()
        
        # 요청 정보 로깅
        client_ip = request.client.host if request.client else "unknown"
        logger.info(
            f"요청 시작: {request.method} {request.url.path}",
            client_ip=client_ip,
            user_agent=request.headers.get("user-agent", "unknown"),
        )
        
        # 요청 처리
        response = await call_next(request)
        
        # 처리 시간 계산
        process_time = time.time() - start_time
        
        # 응답 정보 로깅
        logger.info(
            f"요청 완료: {request.method} {request.url.path}",
            status_code=response.status_code,
            process_time=f"{process_time:.4f}s",
        )
        
        # 처리 시간 헤더 추가
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """에러 처리 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.exception(f"예상치 못한 오류: {str(e)}")
            # 에러는 전역 핸들러에서 처리하도록 재발생
            raise


def setup_middleware(app: FastAPI) -> None:
    """미들웨어 설정"""
    
    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )
    
    # 로깅 미들웨어
    app.add_middleware(LoggingMiddleware)
    
    # 에러 처리 미들웨어
    app.add_middleware(ErrorHandlingMiddleware)
    
    logger.success("미들웨어 설정이 완료되었습니다.")