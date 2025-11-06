"""
Vector Database Service using ChromaDB (Free)
ChromaDB는 완전 무료이며 로컬에서 실행됩니다.
"""

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from backend.core.config import settings

logger = logging.getLogger(__name__)


class VectorDBService:
    """
    ChromaDB를 사용한 벡터 데이터베이스 서비스
    의도별로 다른 컬렉션을 사용합니다.
    """

    def __init__(self):
        """ChromaDB 클라이언트 초기화"""
        # 영구 저장소 설정 (로컬 디스크에 저장)
        persist_directory = Path(settings.CHROMA_PERSIST_DIRECTORY)
        persist_directory.mkdir(parents=True, exist_ok=True)

        # ChromaDB 클라이언트 생성
        self.client = chromadb.PersistentClient(
            path=str(persist_directory),
            settings=ChromaSettings(
                anonymized_telemetry=False,  # 텔레메트리 비활성화
                allow_reset=True
            )
        )

        # 무료 임베딩 모델 사용 (Sentence Transformers)
        # OpenAI 임베딩을 사용하려면 API 키가 필요하므로
        # 무료인 Sentence Transformers를 사용합니다
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="paraphrase-multilingual-mpnet-base-v2"  # 한국어 지원
        )

        # 의도별 컬렉션 초기화
        self.collections = {}
        self._init_collections()

        logger.info(f"ChromaDB initialized at {persist_directory}")

    def _init_collections(self):
        """의도별 컬렉션 초기화"""
        collection_names = {
            "MEDICAL_INFO": f"{settings.CHROMA_COLLECTION_PREFIX}_medical_qa",
            "RESEARCH": f"{settings.CHROMA_COLLECTION_PREFIX}_papers",
            "POLICY": f"{settings.CHROMA_COLLECTION_PREFIX}_guidelines",
            "DIET_INFO": f"{settings.CHROMA_COLLECTION_PREFIX}_diet",
            "WELFARE_INFO": f"{settings.CHROMA_COLLECTION_PREFIX}_welfare",
            "LEARNING": f"{settings.CHROMA_COLLECTION_PREFIX}_quiz",
        }

        for intent, collection_name in collection_names.items():
            try:
                # 컬렉션이 이미 있으면 가져오고, 없으면 생성
                self.collections[intent] = self.client.get_or_create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function,
                    metadata={"intent": intent}
                )
                logger.info(f"Collection '{collection_name}' initialized for intent '{intent}'")
            except Exception as e:
                logger.error(f"Failed to initialize collection '{collection_name}': {e}")

    def add_documents(
        self,
        intent: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """
        문서 추가

        Args:
            intent: 의도 타입 (MEDICAL_INFO, RESEARCH, POLICY 등)
            documents: 저장할 문서 리스트
            metadatas: 각 문서의 메타데이터 (선택사항)
            ids: 문서 ID 리스트 (선택사항, 없으면 자동 생성)

        Returns:
            성공 여부
        """
        try:
            if intent not in self.collections:
                logger.error(f"Unknown intent: {intent}")
                return False

            collection = self.collections[intent]

            # ID가 없으면 자동 생성
            if ids is None:
                import uuid
                ids = [str(uuid.uuid4()) for _ in documents]

            # 메타데이터가 없으면 빈 딕셔너리 생성
            if metadatas is None:
                metadatas = [{} for _ in documents]

            # 문서 추가
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            logger.info(f"Added {len(documents)} documents to {intent} collection")
            return True

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False

    def search(
        self,
        intent: str,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        유사도 검색

        Args:
            intent: 의도 타입
            query: 검색 쿼리
            top_k: 반환할 결과 개수
            filters: 메타데이터 필터 (선택사항)

        Returns:
            검색 결과 리스트
        """
        try:
            if intent not in self.collections:
                logger.error(f"Unknown intent: {intent}")
                return []

            collection = self.collections[intent]

            # 검색 수행
            results = collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filters  # 메타데이터 필터
            )

            # 결과 포맷팅
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                documents = results['documents'][0]
                metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(documents)
                distances = results['distances'][0] if results['distances'] else [0] * len(documents)
                ids = results['ids'][0] if results['ids'] else [''] * len(documents)

                for doc, meta, dist, doc_id in zip(documents, metadatas, distances, ids):
                    formatted_results.append({
                        'id': doc_id,
                        'document': doc,
                        'metadata': meta,
                        'similarity_score': 1 - dist  # 거리를 유사도로 변환
                    })

            logger.info(f"Found {len(formatted_results)} results for query in {intent}")
            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def update_document(
        self,
        intent: str,
        document_id: str,
        document: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        문서 업데이트

        Args:
            intent: 의도 타입
            document_id: 업데이트할 문서 ID
            document: 새로운 문서 내용 (선택사항)
            metadata: 새로운 메타데이터 (선택사항)

        Returns:
            성공 여부
        """
        try:
            if intent not in self.collections:
                logger.error(f"Unknown intent: {intent}")
                return False

            collection = self.collections[intent]

            # 업데이트할 데이터 준비
            update_params = {'ids': [document_id]}
            if document:
                update_params['documents'] = [document]
            if metadata:
                update_params['metadatas'] = [metadata]

            collection.update(**update_params)

            logger.info(f"Updated document {document_id} in {intent} collection")
            return True

        except Exception as e:
            logger.error(f"Failed to update document: {e}")
            return False

    def delete_documents(
        self,
        intent: str,
        document_ids: List[str]
    ) -> bool:
        """
        문서 삭제

        Args:
            intent: 의도 타입
            document_ids: 삭제할 문서 ID 리스트

        Returns:
            성공 여부
        """
        try:
            if intent not in self.collections:
                logger.error(f"Unknown intent: {intent}")
                return False

            collection = self.collections[intent]
            collection.delete(ids=document_ids)

            logger.info(f"Deleted {len(document_ids)} documents from {intent} collection")
            return True

        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            return False

    def get_collection_stats(self, intent: str) -> Dict[str, Any]:
        """
        컬렉션 통계 조회

        Args:
            intent: 의도 타입

        Returns:
            컬렉션 통계 정보
        """
        try:
            if intent not in self.collections:
                return {'error': f'Unknown intent: {intent}'}

            collection = self.collections[intent]
            count = collection.count()

            return {
                'intent': intent,
                'collection_name': collection.name,
                'document_count': count,
                'embedding_model': 'paraphrase-multilingual-mpnet-base-v2'
            }

        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {'error': str(e)}

    def reset_collection(self, intent: str) -> bool:
        """
        컬렉션 초기화 (모든 데이터 삭제)

        Args:
            intent: 의도 타입

        Returns:
            성공 여부
        """
        try:
            if intent not in self.collections:
                logger.error(f"Unknown intent: {intent}")
                return False

            collection_name = self.collections[intent].name

            # 컬렉션 삭제 후 재생성
            self.client.delete_collection(name=collection_name)
            self.collections[intent] = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"intent": intent}
            )

            logger.info(f"Reset collection for intent '{intent}'")
            return True

        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False


# 싱글톤 인스턴스
vector_db = VectorDBService()