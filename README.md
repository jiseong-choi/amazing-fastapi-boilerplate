# AI-Ready FastAPI Boilerplate

🤖 AI 에이전트를 위한 완벽한 FastAPI 보일러플레이트

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.103.1-green.svg)](https://fastapi.tiangolo.com/)

## 🚀 주요 기능

- **AI 에이전트 친화적 API**: OpenAPI 3.1 완전 호환
- **자동 SDK 생성**: OpenAPI 스펙으로 Python/JS/Go SDK 자동 생성
- **스트리밍 지원**: Server-Sent Events (SSE)로 실시간 응답
- **속도 제한**: AI 호출 과부하 방지
- **메타데이터 엔드포인트**: `/v1/agent/capabilities`로 기능 자동 발견
- **샌드박스 환경**: 테스트용 Mock AI 응답

## 📦 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/ai-ready-fastapi.git
cd ai-ready-fastapi

# 가상 환경 생성
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r app/requirements.txt
```

## 🏃‍♂️ 실행

```bash
# 개발 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API 문서 확인
# http://localhost:8000/docs
# http://localhost:8000/redoc
```

## 🤖 AI 에이전트 통합

### Python (LangChain 호환)

```python
import requests
from typing import Dict, Any

class AIAgentClient:
    def __init__(self, base_url: str, api_key: str = None):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key} if api_key else {}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """서버 기능 조회"""
        response = requests.get(
            f"{self.base_url}/v1/agent/capabilities",
            headers=self.headers
        )
        return response.json()
    
    def list_tools(self) -> list:
        """사용 가능한 도구 목록"""
        response = requests.get(
            f"{self.base_url}/v1/agent/tools",
            headers=self.headers
        )
        return response.json()
    
    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """도구 실행"""
        response = requests.post(
            f"{self.base_url}/v1/agent/execute",
            json={"tool_name": tool_name, "parameters": parameters},
            headers=self.headers
        )
        return response.json()

# 사용 예시
client = AIAgentClient("http://localhost:8000")

# 1. 서버 기능 확인
capabilities = client.get_capabilities()
print(f"사용 가능한 도구: {capabilities['tools']}")

# 2. 텍스트 유사도 계산
result = client.execute_tool("text_similarity", {
    "text1": "FastAPI is great",
    "text2": "I love FastAPI"
})
print(f"유사도: {result['result']}")

# 3. 키워드 추출
result = client.execute_tool("extract_keywords", {
    "text": "FastAPI is a modern, fast web framework for building APIs with Python",
    "top_n": 3
})
print(f"키워드: {result['result']}")
```

## 🔐 인증 시스템 (명령어 한 줄로!)

인증 시스템이 완전히 통합되어 있습니다. 다음 명령어로 간단하게 사용할 수 있습니다:

### 1. 사용자 등록 (한 줄 명령어)
```bash
# 사용자 등록
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123", "name": "홍길동"}'
```

### 2. 로그인 (한 줄 명령어)
```bash
# 로그인하고 토큰 받기
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### 3. 내 정보 조회 (한 줄 명령어)
```bash
# 로그인 후 받은 토큰으로 내 정보 조회
curl -X GET "http://localhost:8000/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 4. 토큰 갱신 (한 줄 명령어)
```bash
# 리프레시 토큰으로 새 엑세스 토큰 발급
curl -X POST "http://localhost:8000/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

### 5. 로그아웃 (한 줄 명령어)
```bash
# 로그아웃
curl -X POST "http://localhost:8000/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**💡 팁**: 모든 엔드포인트는 OpenAPI 문서에서 "Try it out" 버튼으로 테스트할 수 있습니다: http://localhost:8000/docs

### JavaScript/TypeScript

```typescript
interface ToolResult {
  success: boolean;
  result: any;
  error?: string;
  metadata: Record<string, any>;
}

class AIAgentClient {
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(baseUrl: string, apiKey?: string) {
    this.baseUrl = baseUrl;
    this.headers = apiKey ? { 'X-API-Key': apiKey } : {};
  }

  async getCapabilities(): Promise<Record<string, any>> {
    const response = await fetch(`${this.baseUrl}/v1/agent/capabilities`, {
      headers: this.headers
    });
    return response.json();
  }

  async executeTool(toolName: string, parameters: Record<string, any>): Promise<ToolResult> {
    const response = await fetch(`${this.baseUrl}/v1/agent/execute`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.headers
      },
      body: JSON.stringify({
        tool_name: toolName,
        parameters: parameters
      })
    });
    return response.json();
  }
}

// 사용 예시
const client = new AIAgentClient('http://localhost:8000');

// 텍스트 유사도 계산
const result = await client.executeTool('text_similarity', {
  text1: 'Hello world',
  text2: 'Hi world'
});
console.log(`유사도: ${result.result}`);
```

### cURL

```bash
# 서버 기능 확인
curl -X GET "http://localhost:8000/v1/agent/capabilities"

# 도구 목록 조회
curl -X GET "http://localhost:8000/v1/agent/tools"

# 도구 실행
curl -X POST "http://localhost:8000/v1/agent/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "text_similarity",
    "parameters": {
      "text1": "FastAPI is awesome",
      "text2": "I love FastAPI"
    }
  }'
```

## 🔧 사용 가능한 도구

| 도구 | 설명 | 파라미터 | 반환값 |
|------|------|----------|--------|
| `text_similarity` | 두 텍스트의 유사도 계산 | `text1`, `text2`, `method` | `float` |
| `extract_keywords` | 텍스트에서 키워드 추출 | `text`, `top_n`, `language` | `list[string]` |
| `summarize_text` | 텍스트 요약 | `text`, `max_length`, `method` | `string` |
| `generate_embedding` | 텍스트 임베딩 생성 | `text`, `model` | `list[float]` |
| `web_search` | 웹 검색 | `query`, `num_results`, `type` | `list[dict]` |

## 📚 API 엔드포인트

### 에이전트 엔드포인트 (`/v1/agent/`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/capabilities` | 서버 기능 조회 |
| GET | `/tools` | 사용 가능한 도구 목록 |
| POST | `/execute` | 도구 실행 |
| GET | `/health` | 서버 상태 확인 |

### 인증

API 키를 사용한 인증을 지원합니다:

```bash
# API 키와 함께 요청
curl -H "X-API-Key: your-api-key" http://localhost:8000/v1/agent/capabilities
```

## 🛠️ 개발

### 테스트

```bash
# API 테스트
pytest tests/

# 단위 테스트
pytest tests/unit/

# 통합 테스트
pytest tests/integration/
```

### Docker

```bash
# Docker 이미지 빌드
docker build -t ai-ready-fastapi .

# 컨테이너 실행
docker run -p 8000:8000 ai-ready-fastapi
```

## 🤝 기여

기여를 환영합니다! 다음 단계를 따라주세요:

1. 저장소 포크
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 커밋 (`git commit -m 'Add amazing feature'`)
4. 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📄 라이선스

MIT 라이선스 - [LICENSE](LICENSE) 파일 참조

## 🙏 감사

- [FastAPI](https://fastapi.tiangolo.com/) - 현대적이고 빠른 웹 프레임워크
- [Pydantic](https://pydantic.dev/) - 데이터 검증 라이브러리
- [Loguru](https://github.com/Delgan/loguru) - 간편한 로깅 라이브러리

---

AI 에이전트 개발자 커뮤니티에 참여하세요! 🚀