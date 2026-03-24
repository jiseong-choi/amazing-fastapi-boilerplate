#!/bin/bash

# AI-Ready FastAPI Boilerplate 시작 스크립트

echo "🚀 AI-Ready FastAPI Boilerplate 시작 중..."

# 가상 환경 확인
if [ ! -d "venv" ]; then
    echo "📦 가상 환경 생성 중..."
    python3 -m venv venv
fi

# 가상 환경 활성화
echo "🔧 가상 환경 활성화..."
source venv/bin/activate

# 의존성 설치
echo "📚 의존성 설치 중..."
pip install -r app/requirements.txt

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. 기본 설정을 사용합니다."
    cat > .env << EOF
OPENAPI_API_NAME = 'AI-Ready API'
OPENAPI_API_VERSION = '1.0.0'
OPENAPI_API_DESCRIPTION = 'AI 에이전트를 위한 완벽한 FastAPI 보일러플레이트'
LOG_LEVEL = 'INFO'
SECRET_KEY = 'change-this-in-production'
EOF
fi

# 서버 시작
echo "🌐 서버 시작 중... (http://localhost:8000)"
echo "📚 API 문서: http://localhost:8000/docs"
echo "🤖 AI Agent 엔드포인트: http://localhost:8000/v1/agent/capabilities"
echo "🔐 인증 엔드포인트: http://localhost:8000/auth/register"
echo ""
echo "서버를 중지하려면 Ctrl+C를 누르세요."

uvicorn main:app --reload --host 0.0.0.0 --port 8000