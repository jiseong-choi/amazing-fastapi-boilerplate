"""전역 예외 처리"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger


class AppException(Exception):
    """애플리케이션 기본 예외"""
    def __init__(
        self,
        message: str = "내부 서버 오류가 발생했습니다.",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class NotFoundException(AppException):
    """리소스를 찾을 수 없는 경우"""
    def __init__(self, message: str = "리소스를 찾을 수 없습니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=404, details=details)


class UnauthorizedException(AppException):
    """인증 실패"""
    def __init__(self, message: str = "인증이 필요합니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=401, details=details)


class ForbiddenException(AppException):
    """권한 없음"""
    def __init__(self, message: str = "접근 권한이 없습니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=403, details=details)


class BadRequestException(AppException):
    """잘못된 요청"""
    def __init__(self, message: str = "잘못된 요청입니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=400, details=details)


class ConflictException(AppException):
    """충돌"""
    def __init__(self, message: str = "리소스 충돌이 발생했습니다.", details: Optional[Dict[str, Any]] = None):
        super().__init__(message=message, status_code=409, details=details)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """애플리케이션 예외 처리기"""
    logger.error(f"애플리케이션 예외 발생: {exc.message}", details=exc.details)
    
    content = {
        "error": {
            "message": exc.message,
            "status_code": exc.status_code,
            "details": exc.details,
        }
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP 예외 처리기"""
    logger.warning(f"HTTP 예외 발생: {exc.detail}", status_code=exc.status_code)
    
    content = {
        "error": {
            "message": exc.detail,
            "status_code": exc.status_code,
        }
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """일반 예외 처리기"""
    logger.exception(f"예상치 못한 오류 발생: {str(exc)}")
    
    content = {
        "error": {
            "message": "내부 서버 오류가 발생했습니다.",
            "status_code": 500,
        }
    }
    
    return JSONResponse(
        status_code=500,
        content=content,
    )