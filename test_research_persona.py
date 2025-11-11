#!/usr/bin/env python3
"""
페르소나 1: 논문 검색 사용자 테스트 스크립트
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_sglt2_research():
    """시나리오 1-A: SGLT2 억제제 논문 검색"""
    print("=" * 80)
    print("🔬 시나리오 1-A: SGLT2 억제제 최신 논문 검색")
    print("=" * 80)

    # 질문
    question = "SGLT2 억제제가 만성 콩팥병 환자에게 효과가 있나요? 최신 논문을 찾아주세요."
    user_id = "researcher_001"

    print(f"\n📝 질문: {question}")
    print(f"👤 사용자: {user_id}\n")

    # API 요청
    payload = {
        "question": question,
        "user_id": user_id
    }

    print("⏳ 요청 전송 중...")
    start_time = datetime.now()

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )

        end_time = datetime.now()
        elapsed = (end_time - start_time).total_seconds()

        response.raise_for_status()
        result = response.json()

        # 결과 출력
        print("\n" + "=" * 80)
        print("✅ 응답 성공")
        print("=" * 80)

        print(f"\n⏱️  처리 시간: {elapsed:.2f}초")
        print(f"🎯 의도: {result['intent']} (신뢰도: {result['intent_confidence']:.2%})")
        print(f"📚 선택된 DB: {', '.join(result['selected_databases'])}")
        print(f"📄 검색된 문서 수: {result['total_documents']}개")

        print("\n" + "-" * 80)
        print("🔍 안전 검사 결과:")
        print(f"  응급 상황: {'❌' if not result['is_emergency'] else '🚨 예'}")
        print(f"  의료 판단 요청: {'❌' if not result['is_medical_judgment'] else '⚠️ 예'}")
        print(f"  안전성: {'✅ 안전' if result['is_safe'] else '❌ 위험'}")

        print("\n" + "-" * 80)
        print("📚 논문 요약:")
        for i, summary in enumerate(result['summaries'][:3], 1):  # 최대 3개만 표시
            print(f"\n{i}️⃣ **{summary['title']}**")
            print(f"   출처: {summary['source']}")
            print(f"   요약: {summary['content'][:200]}...")

        print("\n" + "-" * 80)
        print("💬 최종 응답:")
        print(result['answer'][:500] + "...")

        # 성공 여부 판단
        assert result['intent'] == 'RESEARCH', "❌ 의도 분류 실패"
        assert result['is_safe'] == True, "❌ 안전 검사 실패"
        assert result['total_documents'] > 0, "❌ 문서 검색 실패"
        assert len(result['summaries']) > 0, "❌ 요약 생성 실패"

        print("\n" + "=" * 80)
        print("✅ 시나리오 1-A 테스트 성공!")
        print("=" * 80)

        return True

    except requests.exceptions.RequestException as e:
        print(f"\n❌ 요청 실패: {e}")
        return False
    except AssertionError as e:
        print(f"\n❌ 검증 실패: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        return False


def test_proteinuria_research():
    """시나리오 1-B: 단백뇨 관련 연구"""
    print("\n\n" + "=" * 80)
    print("🔬 시나리오 1-B: 단백뇨 수치 근거 확인")
    print("=" * 80)

    question = "단백뇨 수치가 만성 콩팥병 진행에 어떤 영향을 미치나요? 관련 연구 논문을 알려주세요."
    user_id = "researcher_001"

    print(f"\n📝 질문: {question}")
    print(f"👤 사용자: {user_id}\n")

    payload = {
        "question": question,
        "user_id": user_id
    }

    print("⏳ 요청 전송 중...")

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat",
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        print("\n✅ 응답 성공")
        print(f"🎯 의도: {result['intent']} (신뢰도: {result['intent_confidence']:.2%})")
        print(f"📄 검색된 문서 수: {result['total_documents']}개")

        assert result['intent'] == 'RESEARCH'
        assert result['is_safe'] == True

        print("\n✅ 시나리오 1-B 테스트 성공!")

        return True

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 MockinJay 페르소나 1 테스트 시작\n")

    results = []

    # 시나리오 1-A 실행
    results.append(test_sglt2_research())

    # 시나리오 1-B 실행
    results.append(test_proteinuria_research())

    # 결과 요약
    print("\n\n" + "=" * 80)
    print("📊 테스트 결과 요약")
    print("=" * 80)
    print(f"총 테스트: {len(results)}개")
    print(f"성공: {sum(results)}개")
    print(f"실패: {len(results) - sum(results)}개")

    if all(results):
        print("\n🎉 모든 테스트 통과!")
    else:
        print("\n❌ 일부 테스트 실패")
