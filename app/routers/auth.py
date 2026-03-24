"""인증 관련 API 엔드포인트"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from loguru import logger
import jwt
from passlib.context import CryptContext

from app.config.settings import settings

router = APIRouter(tags=["인증"])

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT 설정
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# 인메모리 사용자 저장소 (실제로는 데이터베이스 사용)
users_db: Dict[str, Dict[str, Any]] = {}


# 데이터 모델
class UserRegister(BaseModel):
    """사용자 등록 요청"""
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., min_length=8, description="비밀번호 (최소 8자)")
    name: str = Field(..., min_length=2, description="이름")

class UserLogin(BaseModel):
    """사용자 로그인 요청"""
    email: EmailStr = Field(..., description="이메일 주소")
    password: str = Field(..., description="비밀번호")

class TokenRefresh(BaseModel):
    """토큰 갱신 요청"""
    refresh_token: str = Field(..., description="리프레시 토큰")

class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str = Field(..., description="엑세스 토큰")
    refresh_token: str = Field(..., description="리프레시 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="엑세스 토큰 만료 시간 (초)")

class UserInfo(BaseModel):
    """사용자 정보"""
    email: str = Field(..., description="이메일 주소")
    name: str = Field(..., description="이름")
    created_at: str = Field(..., description="가입 시간")

class AuthResponse(BaseModel):
    """인증 응답"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="메시지")
    data: Optional[Dict[str, Any]] = Field(default=None, description="응답 데이터")


# 유틸리티 함수
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """비밀번호 검증"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """비밀번호 해싱"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """엑세스 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """리프레시 토큰 생성"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> dict:
    """토큰 검증"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="잘못된 토큰 타입입니다.",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다.",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
        )

# 의존성: 현재 사용자 가져오기
async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """현재 인증된 사용자 정보 반환"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 헤더가 필요합니다.",
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Bearer 인증 방식을 사용해주세요.",
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 인증 헤더 형식입니다.",
        )
    
    payload = verify_token(token, "access")
    email = payload.get("sub")
    if email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
        )
    
    return users_db[email]


# API 엔드포인트
@router.post(
    "/register",
    response_model=AuthResponse,
    summary="사용자 등록",
    description="새로운 사용자를 등록합니다. 이메일과 비밀번호를 입력하면 계정을 생성합니다.",
    responses={
        201: {
            "description": "등록 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "사용자가 성공적으로 등록되었습니다.",
                        "data": {"email": "user@example.com", "name": "홍길동"},
                    }
                }
            },
        },
        400: {"description": "이메일 중복"},
        422: {"description": "입력 데이터 검증 실패"},
    },
)
async def register(user: UserRegister):
    """사용자 등록"""
    # 이메일 중복 확인
    if user.email in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다.",
        )
    
    # 사용자 생성
    hashed_password = get_password_hash(user.password)
    users_db[user.email] = {
        "email": user.email,
        "name": user.name,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow().isoformat(),
    }
    
    logger.info(f"새 사용자 등록: {user.email}")
    
    return AuthResponse(
        success=True,
        message="사용자가 성공적으로 등록되었습니다.",
        data={"email": user.email, "name": user.name},
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="사용자 로그인",
    description="이메일과 비밀번호로 로그인합니다. 성공 시 엑세스 토큰과 리프레시 토큰을 반환합니다.",
    responses={
        200: {
            "description": "로그인 성공",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                    }
                }
            },
        },
        401: {"description": "이메일 또는 비밀번호 불일치"},
    },
)
async def login(user: UserLogin):
    """사용자 로그인"""
    # 사용자 확인
    if user.email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 일치하지 않습니다.",
        )
    
    stored_user = users_db[user.email]
    
    # 비밀번호 확인
    if not verify_password(user.password, stored_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 일치하지 않습니다.",
        )
    
    # 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    logger.info(f"사용자 로그인: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="토큰 갱신",
    description="리프레시 토큰을 사용하여新的 엑세스 토큰을 발급받습니다.",
    responses={
        200: {
            "description": "토큰 갱신 성공",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "expires_in": 1800,
                    }
                }
            },
        },
        401: {"description": "유효하지 않은 리프레시 토큰"},
    },
)
async def refresh_token(token_data: TokenRefresh):
    """토큰 갱신"""
    payload = verify_token(token_data.refresh_token, "refresh")
    email = payload.get("sub")
    
    if email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
        )
    
    # 새로운 엑세스 토큰 생성
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": email},
        expires_delta=access_token_expires,
    )
    
    # 새로운 리프레시 토큰 생성 (선택적)
    refresh_token = create_refresh_token(data={"sub": email})
    
    logger.info(f"토큰 갱신: {email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me",
    response_model=UserInfo,
    summary="현재 사용자 정보",
    description="인증된 사용자의 정보를 반환합니다. Authorization 헤더에 Bearer 토큰을 포함해야 합니다.",
    responses={
        200: {
            "description": "사용자 정보 반환",
            "content": {
                "application/json": {
                    "example": {
                        "email": "user@example.com",
                        "name": "홍길동",
                        "created_at": "2024-01-01T00:00:00",
                    }
                }
            },
        },
        401: {"description": "인증 실패"},
    },
)
async def get_user_info(current_user: dict = Depends(get_current_user)):
    """현재 사용자 정보 조회"""
    return UserInfo(
        email=current_user["email"],
        name=current_user["name"],
        created_at=current_user["created_at"],
    )


@router.post(
    "/logout",
    response_model=AuthResponse,
    summary="사용자 로그아웃",
    description="사용자를 로그아웃합니다. 서버에서는 토큰을 무효화하지만, 클라이언트는 토큰을 삭제해야 합니다.",
    responses={
        200: {
            "description": "로그아웃 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "성공적으로 로그아웃되었습니다.",
                        "data": None,
                    }
                }
            },
        },
        401: {"description": "인증 실패"},
    },
)
async def logout(current_user: dict = Depends(get_current_user)):
    """사용자 로그아웃"""
    logger.info(f"사용자 로그아웃: {current_user['email']}")
    return AuthResponse(
        success=True,
        message="성공적으로 로그아웃되었습니다.",
        data=None,
    )