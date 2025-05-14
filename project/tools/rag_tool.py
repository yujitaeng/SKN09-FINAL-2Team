import os
import traceback
from langchain.tools import Tool                  # Tool 클래스를 사용하기 위함
from langchain_qdrant import Qdrant         # Qdrant 벡터스토어 래퍼
from langchain_huggingface import HuggingFaceEmbeddings  # 임베딩 모델
from qdrant_client import QdrantClient
from pathlib import Path                             # 상대 경로를 사용하기 위함


# 상대 경로 기반 Qdrant 경로 지정
base_path = Path(__file__).resolve().parent.parent
qdrant = QdrantClient(path=str(base_path / "qdrant"))

embedding = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large-instruct")

vectorstore = Qdrant(
    client=qdrant,
    collection_name="my_documents",
    embeddings=embedding,
    content_payload_key="page_content",  # ✅ 반드시 저장한 필드명과 일치해야 함
)


def retrieve_from_qdrant(query: str) -> str:
    try:
        # 검색 결과 수 5개로 확장, 더 다양한 결과 제공
        results = vectorstore.similarity_search(query, k=20)
        
        # 결과가 없으면 빈 문자열 반환
        if not results:
            return ""
        
        # 결과 포맷팅: 각 문서에 대한 상세 정보 제공
        formatted_results = []
        for i, doc in enumerate(results, 1):
            formatted_result = f"[결과 {i}]\n내용: {doc.page_content}\n유사도: {doc.metadata.get('similarity', '알 수 없음')}"
            formatted_results.append(formatted_result)
        
        return "\n\n".join(formatted_results)
    except Exception as e:
        print(f"RAG 검색 중 오류 발생: {e}")
        return ""

qdrant_rag_tool = Tool(
    name="QdrantSearch",
    func=retrieve_from_qdrant,
    description="KoSBERT 기반 Qdrant에서 유사 문서를 검색합니다. 문서 기반 질문에 사용하세요."
)

__all__ = ["qdrant_rag_tool"]