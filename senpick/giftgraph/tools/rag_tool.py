from langchain.tools import Tool, StructuredTool
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from pydantic import BaseModel, Field

import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

if os.getenv("ENVIRONMENT") == "PRODUCTION":
    qdrant = QdrantClient(url="http://qdrant:6333", prefer_grpc=False)
else:
    qdrant = QdrantClient(url="http://localhost:6333", prefer_grpc=False)
embedding = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large-instruct")
vectorstore = QdrantVectorStore(
    client=qdrant,
    collection_name="senpick",
    embedding=embedding,
)

def retrieve_from_qdrant(query: str, min_price:int=0, max_price:int=1000000) -> list[dict]:
    try:
        results = vectorstore.similarity_search_with_score(
            query, 
            k=10,
            filter={
                "must": [
                    {"key": "price", "range": {"gte": min_price, "lte": max_price}},  # 기본 가격 범위
                ],
            }
        )
        if not results:
            return []

        observations = []
        for doc, score in results:
            metadata = doc.metadata
            observations.append({
                "brand": metadata.get("brand", "브랜드 정보 없음"),
                "title": metadata.get("title", "이름 없음"),
                "price": metadata.get("price", 0),
                "imageUrl": metadata.get("thumbnail_url", ""),
                "link": metadata.get("product_url", "")
            })
        return observations
    except Exception as e:
        print(f"RAG 검색 중 오류 발생: {e}")
        return []

# — 파라미터 명세는 그대로 사용
class RAGQuery(BaseModel):
    query: str = Field(..., description="사용자의 요청 내용 또는 검색 키워드")
    min_price: int = Field(10000, description="검색할 최소 가격 (원)")
    max_price: int = Field(50000, description="검색할 최대 가격 (원)")

# — StructuredTool로 등록
rag_tool = StructuredTool(
    name="rag_tool",
    func=retrieve_from_qdrant,       # 시그니처: (query, min_price, max_price)
    description=(
        "Qdrant에서 유사한 선물/제품 정보를 검색합니다.\n"
        "- query: 상황, 감정, 스타일 등 검색 키워드\n"
        "- min_price/max_price: 희망 가격 범위 (단위: 원)\n"
        "가격 정보가 없으면 기본값(1~5만원)을 사용하세요."
    ),
    args_schema=RAGQuery
)
__all__ = ["rag_tool"]