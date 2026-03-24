"""AI 에이전트를 위한 API 엔드포인트"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from loguru import logger

router = APIRouter(tags=["AI Agent"])


# 데이터 모델 정의
class ToolParameter(BaseModel):
    """도구 매개변수 정의"""
    name: str = Field(..., description="매개변수 이름")
    type: str = Field(..., description="매개변수 타입 (string, number, boolean, object, array)")
    description: str = Field(..., description="매개변수 설명")
    required: bool = Field(default=False, description="필수 여부")
    default: Optional[Any] = Field(default=None, description="기본값")


class ToolDefinition(BaseModel):
    """도구 정의"""
    name: str = Field(..., description="도구 고유 이름")
    description: str = Field(..., description="도구 기능 설명")
    parameters: List[ToolParameter] = Field(default_factory=list, description="매개변수 목록")
    return_type: str = Field(..., description="반환값 타입")
    examples: List[Dict[str, Any]] = Field(default_factory=list, description="사용 예제")


class ToolExecutionRequest(BaseModel):
    """도구 실행 요청"""
    tool_name: str = Field(..., description="실행할 도구 이름")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="매개변수 딕셔너리")
    context: Optional[Dict[str, Any]] = Field(default=None, description="실행 컨텍스트")


class ToolExecutionResponse(BaseModel):
    """도구 실행 응답"""
    success: bool = Field(..., description="실행 성공 여부")
    result: Any = Field(..., description="실행 결과")
    error: Optional[str] = Field(default=None, description="에러 메시지")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="메타데이터")


class AgentCapabilities(BaseModel):
    """에이전트 capabilities"""
    version: str = Field(..., description="API 버전")
    capabilities: List[str] = Field(..., description="서버가 지원하는 기능 목록")
    tools: List[str] = Field(..., description="사용 가능한 도구 목록")
    rate_limits: Dict[str, int] = Field(..., description="속도 제한 정보")
    authentication: List[str] = Field(..., description="지원하는 인증 방식")


# 실제 도구 구현 (예시)
AVAILABLE_TOOLS = {
    "text_similarity": ToolDefinition(
        name="text_similarity",
        description="두 텍스트의 유사도를 계산합니다. 코사인 유사도를 사용하며, 0~1 사이의 값을 반환합니다.",
        parameters=[
            ToolParameter(name="text1", type="string", description="첫 번째 텍스트", required=True),
            ToolParameter(name="text2", type="string", description="두 번째 텍스트", required=True),
            ToolParameter(name="method", type="string", description="유사도 계산 방법", required=False, default="cosine"),
        ],
        return_type="float",
        examples=[
            {"text1": "Hello world", "text2": "Hi world", "method": "cosine"},
            {"text1": "FastAPI is great", "text2": "I love FastAPI", "method": "cosine"},
        ],
    ),
    "extract_keywords": ToolDefinition(
        name="extract_keywords",
        description="텍스트에서 키워드를 추출합니다. TF-IDF 알고리즘을 사용하며, 상위 N개의 키워드를 반환합니다.",
        parameters=[
            ToolParameter(name="text", type="string", description="키워드를 추출할 텍스트", required=True),
            ToolParameter(name="top_n", type="number", description="반환할 키워드 수", required=False, default=5),
            ToolParameter(name="language", type="string", description="텍스트 언어", required=False, default="auto"),
        ],
        return_type="list[string]",
        examples=[
            {"text": "FastAPI is a modern, fast web framework for building APIs with Python", "top_n": 3},
        ],
    ),
    "summarize_text": ToolDefinition(
        name="summarize_text",
        description="긴 텍스트를 요약합니다. 추출적 요약과 추론적 요약을 지원합니다.",
        parameters=[
            ToolParameter(name="text", type="string", description="요약할 텍스트", required=True),
            ToolParameter(name="max_length", type="number", description="최대 요약 길이", required=False, default=100),
            ToolParameter(name="method", type="string", description="요약 방법 (extractive/abstractive)", required=False, default="extractive"),
        ],
        return_type="string",
        examples=[
            {"text": "긴 텍스트 예시...", "max_length": 50, "method": "extractive"},
        ],
    ),
    "generate_embedding": ToolDefinition(
        name="generate_embedding",
        description="텍스트를 벡터 임베딩으로 변환합니다. AI 검색 및 유사도 계산에 사용됩니다.",
        parameters=[
            ToolParameter(name="text", type="string", description="임베딩할 텍스트", required=True),
            ToolParameter(name="model", type="string", description="임베딩 모델", required=False, default="default"),
        ],
        return_type="list[float]",
        examples=[
            {"text": "This is a test sentence", "model": "default"},
        ],
    ),
    "web_search": ToolDefinition(
        name="web_search",
        description="웹에서 정보를 검색합니다. 뉴스, 논문, 일반 정보 등을 검색할 수 있습니다.",
        parameters=[
            ToolParameter(name="query", type="string", description="검색어", required=True),
            ToolParameter(name="num_results", type="number", description="반환할 결과 수", required=False, default=5),
            ToolParameter(name="type", type="string", description="검색 유형 (news, academic, general)", required=False, default="general"),
        ],
        return_type="list[dict]",
        examples=[
            {"query": "FastAPI tutorial", "num_results": 3, "type": "general"},
        ],
    ),
}


# API 키 인증 의존성
async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """API 키 검증"""
    from app.config.settings import settings
    
    if x_api_key is None:
        if settings.REQUIRE_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API 키가 필요합니다. 'X-API-Key' 헤더를 제공해주세요.",
            )
        else:
            logger.warning("API 키가 제공되지 않았습니다. 개발 모드에서 실행 중입니다.")
            return None
    
    if x_api_key in settings.API_KEYS:
        return x_api_key
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 API 키입니다.",
    )


@router.get(
    "/capabilities",
    response_model=AgentCapabilities,
    summary="서버 capabilities 조회",
    description="이 서버가 지원하는 모든 기능과 도구 목록을 반환합니다. AI 에이전트는 이 정보를 사용하여 가능한 작업을 파악합니다.",
    responses={
        200: {
            "description": "서버 capabilities 정보",
            "content": {
                "application/json": {
                    "example": {
                        "version": "1.0.0",
                        "capabilities": ["text_processing", "web_search", "data_analysis"],
                        "tools": ["text_similarity", "extract_keywords", "summarize_text"],
                        "rate_limits": {"requests_per_minute": 60, "requests_per_day": 1000},
                        "authentication": ["api_key", "bearer_token"],
                    }
                }
            },
        }
    },
)
async def get_capabilities(api_key: Optional[str] = Depends(verify_api_key)):
    """서버가 지원하는 capabilities와 도구 목록을 반환합니다."""
    return AgentCapabilities(
        version="1.0.0",
        capabilities=["text_processing", "web_search", "data_analysis", "embedding_generation"],
        tools=list(AVAILABLE_TOOLS.keys()),
        rate_limits={"requests_per_minute": 60, "requests_per_day": 1000},
        authentication=["api_key", "bearer_token"],
    )


@router.get(
    "/tools",
    response_model=List[ToolDefinition],
    summary="사용 가능한 도구 목록",
    description="이 서버에서 사용할 수 있는 모든 도구의 상세 정보를 반환합니다. 각 도구의 매개변수와 사용법을 포함합니다.",
    responses={
        200: {
            "description": "도구 목록",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "name": "text_similarity",
                            "description": "두 텍스트의 유사도를 계산합니다.",
                            "parameters": [
                                {
                                    "name": "text1",
                                    "type": "string",
                                    "description": "첫 번째 텍스트",
                                    "required": True,
                                }
                            ],
                            "return_type": "float",
                            "examples": [{"text1": "Hello", "text2": "Hi"}],
                        }
                    ]
                }
            },
        }
    },
)
async def list_tools(api_key: Optional[str] = Depends(verify_api_key)):
    """모든 도구의 상세 정보를 반환합니다."""
    return list(AVAILABLE_TOOLS.values())


@router.post(
    "/execute",
    response_model=ToolExecutionResponse,
    summary="도구 실행",
    description="지정된 도구를 주어진 매개변수로 실행합니다. AI 에이전트는 이 엔드포인트를 통해 실제 작업을 수행합니다.",
    responses={
        200: {
            "description": "도구 실행 성공",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "result": 0.85,
                        "error": None,
                        "metadata": {"execution_time": 0.05, "tool_version": "1.0"},
                    }
                }
            },
        },
        400: {"description": "잘못된 요청"},
        404: {"description": "도구를 찾을 수 없음"},
        422: {"description": "매개변수 검증 실패"},
    },
)
async def execute_tool(
    request: ToolExecutionRequest,
    api_key: Optional[str] = Depends(verify_api_key),
):
    """도구를 실행하고 결과를 반환합니다."""
    # 도구 존재 확인
    if request.tool_name not in AVAILABLE_TOOLS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"도구 '{request.tool_name}'을(를) 찾을 수 없습니다.",
        )
    
    tool_def = AVAILABLE_TOOLS[request.tool_name]
    
    # 필수 매개변수 검증
    required_params = [p.name for p in tool_def.parameters if p.required]
    for param in required_params:
        if param not in request.parameters:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"필수 매개변수 '{param}'이(가) 누락되었습니다.",
            )
    
    try:
        # 실제 도구 실행 (예시)
        result = None
        if request.tool_name == "text_similarity":
            # 간단한 유사도 계산 예시
            text1 = request.parameters.get("text1", "")
            text2 = request.parameters.get("text2", "")
            # 간단한 단어 기반 유사도 (실제로는 임베딩 사용)
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            result = intersection / union if union > 0 else 0.0
            
        elif request.tool_name == "extract_keywords":
            # 키워드 추출 예시
            text = request.parameters.get("text", "")
            top_n = request.parameters.get("top_n", 5)
            # 간단한 단어 빈도 기반
            words = text.lower().split()
            from collections import Counter
            word_counts = Counter(words)
            result = [word for word, count in word_counts.most_common(top_n)]
            
        elif request.tool_name == "summarize_text":
            # 요약 예시
            text = request.parameters.get("text", "")
            max_length = request.parameters.get("max_length", 100)
            result = text[:max_length] + "..." if len(text) > max_length else text
            
        elif request.tool_name == "generate_embedding":
            # 임베딩 예시 (랜덤)
            import random
            result = [random.random() for _ in range(128)]
            
        elif request.tool_name == "web_search":
            # 웹 검색 예시
            query = request.parameters.get("query", "")
            num_results = request.parameters.get("num_results", 5)
            result = [
                {"title": f"Result {i+1} for '{query}'", "url": f"https://example.com/{i}", "snippet": "..."}
                for i in range(num_results)
            ]
        
        return ToolExecutionResponse(
            success=True,
            result=result,
            error=None,
            metadata={
                "execution_time": 0.05,
                "tool_version": "1.0",
                "api_key_used": api_key is not None,
            },
        )
        
    except Exception as e:
        logger.error(f"도구 실행 중 오류: {e}")
        return ToolExecutionResponse(
            success=False,
            result=None,
            error=str(e),
            metadata={"error_type": type(e).__name__},
        )


@router.get(
    "/health",
    summary="서버 상태 확인",
    description="서버의 현재 상태를 확인합니다. AI 에이전트는 연결 테스트에 사용할 수 있습니다.",
    responses={
        200: {
            "description": "서버 상태 정상",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "version": "1.0.0",
                        "timestamp": "2024-01-01T00:00:00Z",
                        "uptime": 12345,
                    }
                }
            },
        }
    },
)
async def health_check():
    """서버 상태를 확인합니다."""
    import time
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "uptime": 12345,  # 실제 구현에서는 서버 시작 시간부터의 경과 시간
        "tools_available": len(AVAILABLE_TOOLS),
    }