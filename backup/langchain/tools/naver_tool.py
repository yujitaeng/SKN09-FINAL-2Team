#websearch tool
import os                                     # 환경변수 접근용 (.env)
import re                                     # HTML 태그 제거용
import requests                               # HTTP 요청 (Naver API 호출)
from langchain.tools import Tool              # LangChain Tool 정의
from langchain_openai import ChatOpenAI  # LLM 호출용
from dotenv import load_dotenv                # .env 환경변수 로딩
from pathlib import Path                      # 상대 경로를 사용하기 위함


base_path = Path(__file__).resolve().parent.parent  # tools/의 상위 → project/
env_path = base_path / ".env"   
load_dotenv()

CLIENT_ID = os.environ['NAVER_CLIENT_ID']
CLIENT_SECRET = os.environ['NAVER_CLIENT_SECRET']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
               # project/.env

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

def naver_shop_search(user_input: str) -> str:
    # Step 1: 자연어를 검색용 쿼리로 변환
    prompt = f"""
    사용자가 상품을 요청했지만 내부 DB에는 적절한 결과가 없었습니다.
    아래 문장을 네이버 쇼핑에서 검색하기에 적합한 **간결하고 핵심적인 검색어**로 변환해 주세요.

    입력: "{user_input}"
    출력:
    """
    try:
        search_query = llm.invoke(prompt).content.strip()
    except Exception as e:
        return f"쿼리 정제 중 오류가 발생했습니다: {e}"

    # Step 2: 네이버 쇼핑 검색 API 호출
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    params = {
        "query": search_query,
        "display": 5,    # 상품 5개 가져옴
        "start": 1,
        "sort": "sim"
    }

    url = "https://openapi.naver.com/v1/search/shop.json"
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code != 200:
        return "\n상품 검색 중 오류가 발생했습니다.\n"

    items = response.json().get("items", [])
    if not items:
        return "\n검색 결과가 없습니다.\n"

    result = f"\n🔍 검색어: {search_query}\n\n"
    for item in items:
        title = re.sub(r'<.*?>', '', item['title'])
        price = item['lprice']
        link = item['link']
        image = item['image'] 
        result += f"📌 {title} - {price}원\n🔗 {link}\n🖼️ 이미지: {image}\n\n"

    return result.strip()
naver_tool = Tool(
    name="naver_search",
    func=naver_shop_search,
    description="네이버 쇼핑에서 실시간으로 외부 상품을 검색합니다."

)



__all__ = ["naver_tool"]