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

def retrieve_from_qdrant(query: str) -> str:
    try:
        results = vectorstore.similarity_search_with_score(query, k=4)
        if not results:
            return ""
        formatted_results = []
        for i, doc in enumerate(results, 1):
            formatted_result = f"{doc[0].page_content}"
            formatted_results.append(formatted_result)
        return "\n\n".join(formatted_results)
    except Exception as e:
        print(f"RAG 검색 중 오류 발생: {e}")
        return ""

rag_tool = Tool(
    name="rag_tool",
    func=retrieve_from_qdrant,
    description="Qdrant에서 유사 문서를 검색합니다. (리뷰/감정/분위기 중심 검색)"
)
__all__ = ["rag_tool"]