from langchain.tools import Tool
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient

qdrant = QdrantClient(url="http://localhost:6333", prefer_grpc=False)
embedding = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large-instruct")
vectorstore = QdrantVectorStore(
    client=qdrant,
    collection_name="senpick",
    embedding=embedding,
)

def retrieve_from_qdrant(query: str) -> list[dict]:
    try:
        results = vectorstore.similarity_search_with_score(query, k=10)
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


rag_tool = Tool(
    name="rag_tool",
    func=retrieve_from_qdrant,
    description="Qdrant에서 유사 문서를 검색합니다. (리뷰/감정/분위기 중심 검색)"
)
__all__ = ["rag_tool"]