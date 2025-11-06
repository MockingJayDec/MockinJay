#!/bin/bash

# ChromaDB 설정 및 테스트 스크립트

echo "=================================================="
echo "ChromaDB Vector Database Setup"
echo "=================================================="

# Python 환경 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3가 설치되지 않았습니다"
    exit 1
fi

echo "✅ Python3 확인됨"

# 가상환경 생성 (없으면)
if [ ! -d "venv" ]; then
    echo "📦 가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
echo "🔄 가상환경 활성화..."
source venv/bin/activate

# ChromaDB 설치
echo "📦 ChromaDB 설치 중..."
pip install chromadb==0.4.22 sentence-transformers

# 다른 필요한 패키지 설치
echo "📦 기타 패키지 설치 중..."
pip install -q fastapi uvicorn pydantic python-dotenv loguru

# ChromaDB 데이터 디렉토리 생성
echo "📁 데이터 디렉토리 생성..."
mkdir -p data/chroma_db

echo ""
echo "=================================================="
echo "설치 완료! 테스트 실행"
echo "=================================================="

# 테스트 실행
echo "🧪 Vector DB 테스트 시작..."
python tests/test_vector_db.py

echo ""
echo "=================================================="
echo "설정 완료!"
echo "=================================================="
echo ""
echo "🎉 ChromaDB가 성공적으로 설정되었습니다!"
echo ""
echo "📌 다음 명령으로 서버를 시작할 수 있습니다:"
echo "   uvicorn backend.main:app --reload"
echo ""
echo "📌 API 문서는 다음 주소에서 확인할 수 있습니다:"
echo "   http://localhost:8000/docs"
echo ""
echo "📌 Vector DB 엔드포인트:"
echo "   - POST /api/v1/vector/add - 문서 추가"
echo "   - POST /api/v1/vector/search - 유사도 검색"
echo "   - POST /api/v1/vector/load-sample-data - 샘플 데이터 로드"
echo "   - GET  /api/v1/vector/stats/{intent} - 통계 조회"
echo ""