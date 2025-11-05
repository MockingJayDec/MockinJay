# 환자, 연구자의 질문에 따라 답변하는 의료 챗봇을 위한 질문과 답변의 정확성 검증

## keyword: agent, llm

## 기능1: 질문에 따른 질문의도 예측
input: 질문
output: 질문의도

prompt strategy: few shot 으로 질문의도, 설명, 예시 발화
few shot json example:
{질문의도: “RESEARCH”, 설명:”논문 검색 요청”, 예시 발화: “CKD 최신 연구”, “논문 찾아줘”, 처리 방법: “조건부 PubMed검색”}

예시1
input: 신장병 관련 논문 궁금해
output: RESEARCH


## 기능2: 질문의도에 따른 임베딩 벡터 DB예측
input: 질문의도, 처리방법
output: 선택된 임베딩 벡터 DB

질문의도에 따라 여러 임베딩 벡터 DB중에서 유사도 측정
일정 threshold 넘어가는 DB들을 선택
qna, paper 임베딩 벡터 DB 생성할 예정
DB는 한 개 이상 선택될 수 있음

예시1
input: “RESEARCH”, “조건부 PubMed검색”
output: paper 임베딩 벡터 DB 선택


## 기능3: RAG
input: 기능1에서 질문, 선택된 DB 
output: 거리가 가까운 논문 5개 추천


## 기능4: 요약
input: 거리가 가까운 논문 5개 추천
output: 5개 요약

## 기능5: 휴먼 피드백 데이터 모음
앞 기능들에서 나온 output들을 모두 모음

## 기능6: 휴먼 피드백 사이트
기능1의 질문과 기능4의 요약을 가장 앞 두 컬럼 
다음 컬럼은 질문과 답변에 대한 평가를 내릴 수 있게 평가컬럼이 존재
평가 컬럼에는 버튼이 존재
버튼 3개는 Good, 판단어려움, Bad 
버튼을 누르게 되면 기능5의 데이터에 버튼의 내용이 기능5의 3번째 순서로 저장됨
순서: 기능1의 질문, 기능4의 요약, 평가, 나머지 


