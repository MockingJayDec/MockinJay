"""
샘플 데이터 로더
초기 데이터를 ChromaDB에 로드하는 유틸리티
"""

from typing import List, Dict, Any
import json
import logging
from pathlib import Path
from backend.services.vector_db import vector_db
from backend.core.config import settings

logger = logging.getLogger(__name__)


class DataLoader:
    """초기 데이터 로더"""

    def __init__(self):
        self.data_dir = settings.DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def load_sample_medical_qa(self) -> bool:
        """
        CKD 관련 Q&A 샘플 데이터 로드
        실제 서비스에서는 의료 전문가가 검증한 데이터를 사용해야 합니다.
        """
        sample_qa_data = [
            {
                "id": "qa_001",
                "question": "크레아티닌 수치가 높다는 것은 무엇을 의미하나요?",
                "answer": "크레아티닌은 근육 대사의 부산물로, 신장을 통해 배출됩니다. 수치가 높다는 것은 신장 기능이 저하되었을 가능성을 시사합니다. 정확한 진단은 의사와 상담하세요.",
                "metadata": {
                    "category": "검사",
                    "stage": "all",
                    "keywords": ["크레아티닌", "검사", "신장기능"]
                }
            },
            {
                "id": "qa_002",
                "question": "GFR(사구체여과율)이란 무엇인가요?",
                "answer": "GFR은 신장이 1분 동안 여과하는 혈액의 양을 나타냅니다. 정상 수치는 90 이상이며, 수치가 낮을수록 신장 기능이 저하된 것입니다. 정기적인 검사로 추적 관찰이 중요합니다.",
                "metadata": {
                    "category": "검사",
                    "stage": "all",
                    "keywords": ["GFR", "사구체여과율", "신장기능"]
                }
            },
            {
                "id": "qa_003",
                "question": "CKD 3기 환자는 어떤 음식을 피해야 하나요?",
                "answer": "일반적으로 고칼륨 식품(바나나, 오렌지, 토마토), 고인 식품(유제품, 콩류), 고나트륨 식품을 제한해야 합니다. 개인별 상태가 다르므로 영양사와 상담하여 맞춤 식단을 계획하세요.",
                "metadata": {
                    "category": "식단",
                    "stage": "3",
                    "keywords": ["식단", "음식제한", "CKD3기"]
                }
            },
            {
                "id": "qa_004",
                "question": "혈액투석과 복막투석의 차이는 무엇인가요?",
                "answer": "혈액투석은 병원에서 기계를 통해 혈액을 정화하며 주 3회 시행합니다. 복막투석은 복강 내 투석액을 주입하여 집에서도 가능합니다. 각각 장단점이 있으므로 의료진과 상담하여 결정하세요.",
                "metadata": {
                    "category": "치료",
                    "stage": "5",
                    "keywords": ["투석", "혈액투석", "복막투석", "신대체요법"]
                }
            },
            {
                "id": "qa_005",
                "question": "CKD 환자가 운동을 해도 되나요?",
                "answer": "적절한 운동은 CKD 환자에게 도움이 됩니다. 걷기, 수영, 자전거 타기 같은 유산소 운동을 권장합니다. 단, 과도한 운동은 피하고, 운동 전후 충분한 수분 섭취가 중요합니다. 의사와 상담 후 운동 계획을 세우세요.",
                "metadata": {
                    "category": "생활습관",
                    "stage": "all",
                    "keywords": ["운동", "생활습관", "건강관리"]
                }
            },
            {
                "id": "qa_006",
                "question": "만성콩팥병 진행을 늦추는 방법은?",
                "answer": "혈압과 혈당 관리, 저단백 식이, 금연, 적정 체중 유지, 신독성 약물 회피, 정기 검진이 중요합니다. 의사 처방을 잘 따르고 생활습관을 개선하면 진행을 늦출 수 있습니다.",
                "metadata": {
                    "category": "관리",
                    "stage": "all",
                    "keywords": ["진행지연", "관리", "생활습관"]
                }
            },
            {
                "id": "qa_007",
                "question": "CKD 환자의 빈혈은 왜 생기나요?",
                "answer": "신장은 적혈구 생성을 촉진하는 에리스로포이에틴을 생산합니다. CKD로 이 호르몬 생산이 감소하면 빈혈이 발생합니다. 철분제나 조혈제 치료가 필요할 수 있으니 의사와 상담하세요.",
                "metadata": {
                    "category": "합병증",
                    "stage": "3-5",
                    "keywords": ["빈혈", "합병증", "에리스로포이에틴"]
                }
            },
            {
                "id": "qa_008",
                "question": "칼륨이 높으면 어떤 증상이 나타나나요?",
                "answer": "근육 무력감, 피로감, 불규칙한 심장박동, 저림 등이 나타날 수 있습니다. 심한 경우 심정지 위험이 있으므로 정기 검사와 식이 조절이 중요합니다. 증상이 있으면 즉시 병원을 방문하세요.",
                "metadata": {
                    "category": "증상",
                    "stage": "3-5",
                    "keywords": ["고칼륨혈증", "증상", "합병증"]
                }
            },
            {
                "id": "qa_009",
                "question": "신장이식 대기 기간은 얼마나 되나요?",
                "answer": "혈액형, 조직적합성, 대기 순서 등에 따라 다릅니다. 평균 3-5년이지만 개인차가 큽니다. 생체 기증자가 있으면 더 빨리 이식이 가능합니다. 이식 코디네이터와 상담하세요.",
                "metadata": {
                    "category": "이식",
                    "stage": "5",
                    "keywords": ["신장이식", "대기기간", "이식"]
                }
            },
            {
                "id": "qa_010",
                "question": "CKD 환자가 코로나19 백신을 맞아도 되나요?",
                "answer": "CKD 환자는 코로나19 고위험군이므로 백신 접종이 권장됩니다. 면역억제제 복용 중이면 효과가 낮을 수 있으나 접종이 필요합니다. 접종 시기와 종류는 주치의와 상담하세요.",
                "metadata": {
                    "category": "예방접종",
                    "stage": "all",
                    "keywords": ["코로나19", "백신", "예방접종"]
                }
            }
        ]

        try:
            # 문서와 메타데이터 분리
            documents = []
            metadatas = []
            ids = []

            for qa in sample_qa_data:
                # Q&A를 하나의 문서로 결합
                doc_text = f"질문: {qa['question']}\n답변: {qa['answer']}"
                documents.append(doc_text)
                metadatas.append(qa['metadata'])
                ids.append(qa['id'])

            # ChromaDB에 추가
            success = vector_db.add_documents(
                intent="MEDICAL_INFO",
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            if success:
                logger.info(f"Successfully loaded {len(documents)} QA pairs")
                return True
            else:
                logger.error("Failed to load QA data")
                return False

        except Exception as e:
            logger.error(f"Error loading QA data: {e}")
            return False

    def load_sample_research_papers(self) -> bool:
        """연구 논문 샘플 데이터 로드"""
        sample_papers = [
            {
                "id": "paper_001",
                "title": "Chronic Kidney Disease Management in Primary Care",
                "authors": "Kim et al.",
                "year": 2023,
                "abstract": "This study examines the effectiveness of primary care interventions in managing CKD progression...",
                "doi": "10.1234/sample.001",
                "metadata": {
                    "journal": "Korean Journal of Nephrology",
                    "keywords": ["CKD", "primary care", "management"],
                    "type": "clinical_study"
                }
            },
            {
                "id": "paper_002",
                "title": "Dietary Interventions for CKD Stage 3-4 Patients",
                "authors": "Lee et al.",
                "year": 2023,
                "abstract": "Low-protein diets supplemented with ketoanalogues showed significant benefits in delaying CKD progression...",
                "doi": "10.1234/sample.002",
                "metadata": {
                    "journal": "Nutrition in Clinical Practice",
                    "keywords": ["diet", "protein restriction", "CKD"],
                    "type": "clinical_trial"
                }
            },
            {
                "id": "paper_003",
                "title": "Novel Biomarkers for Early CKD Detection",
                "authors": "Park et al.",
                "year": 2024,
                "abstract": "We identified three novel urinary biomarkers that can predict CKD progression 2 years earlier than traditional markers...",
                "doi": "10.1234/sample.003",
                "metadata": {
                    "journal": "Nature Medicine",
                    "keywords": ["biomarkers", "early detection", "diagnosis"],
                    "type": "research"
                }
            }
        ]

        try:
            documents = []
            metadatas = []
            ids = []

            for paper in sample_papers:
                # 논문 정보를 문서로 포맷팅
                doc_text = f"""Title: {paper['title']}
Authors: {paper['authors']}
Year: {paper['year']}
Abstract: {paper['abstract']}
DOI: {paper['doi']}"""
                documents.append(doc_text)
                metadatas.append(paper['metadata'])
                ids.append(paper['id'])

            success = vector_db.add_documents(
                intent="RESEARCH",
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            if success:
                logger.info(f"Successfully loaded {len(documents)} research papers")
                return True
            else:
                logger.error("Failed to load research papers")
                return False

        except Exception as e:
            logger.error(f"Error loading research papers: {e}")
            return False

    def load_sample_policy_guidelines(self) -> bool:
        """정책/가이드라인 샘플 데이터 로드"""
        sample_guidelines = [
            {
                "id": "policy_001",
                "title": "대한신장학회 CKD 진료지침 2023",
                "content": "CKD 단계별 관리: 1-2기는 원인 질환 치료 중심, 3기부터 합병증 관리, 4-5기는 신대체요법 준비...",
                "metadata": {
                    "organization": "대한신장학회",
                    "year": 2023,
                    "type": "clinical_guideline",
                    "keywords": ["진료지침", "관리", "단계별"]
                }
            },
            {
                "id": "policy_002",
                "title": "CKD 환자 응급상황 대응 지침",
                "content": "호흡곤란, 흉통, 의식저하 시 즉시 119 신고. 고칼륨혈증 증상(근무력, 부정맥) 발견 시 응급실 방문...",
                "metadata": {
                    "organization": "보건복지부",
                    "year": 2023,
                    "type": "emergency_protocol",
                    "keywords": ["응급", "119", "고칼륨혈증"]
                }
            },
            {
                "id": "policy_003",
                "title": "의학적 판단 제한 원칙",
                "content": "AI 챗봇은 진단, 처방, 치료법 결정을 할 수 없음. 모든 의학적 결정은 의사와 상담 필수...",
                "metadata": {
                    "organization": "식품의약품안전처",
                    "year": 2024,
                    "type": "ai_ethics",
                    "keywords": ["AI윤리", "진단금지", "의사상담"]
                }
            }
        ]

        try:
            documents = []
            metadatas = []
            ids = []

            for guideline in sample_guidelines:
                doc_text = f"{guideline['title']}\n\n{guideline['content']}"
                documents.append(doc_text)
                metadatas.append(guideline['metadata'])
                ids.append(guideline['id'])

            success = vector_db.add_documents(
                intent="POLICY",
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            if success:
                logger.info(f"Successfully loaded {len(documents)} policy guidelines")
                return True
            else:
                logger.error("Failed to load policy guidelines")
                return False

        except Exception as e:
            logger.error(f"Error loading policy guidelines: {e}")
            return False

    def load_all_sample_data(self) -> Dict[str, bool]:
        """모든 샘플 데이터 로드"""
        results = {
            "medical_qa": self.load_sample_medical_qa(),
            "research_papers": self.load_sample_research_papers(),
            "policy_guidelines": self.load_sample_policy_guidelines()
        }

        logger.info(f"Sample data loading results: {results}")
        return results


# 싱글톤 인스턴스
data_loader = DataLoader()