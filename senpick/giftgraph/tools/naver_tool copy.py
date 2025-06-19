
import os, re, requests, random                              
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv                
from pathlib import Path                                      

base_path = Path(__file__).resolve().parent.parent  # tools/의 상위 → project/
env_path = base_path / ".env"   
load_dotenv()

CLIENT_ID = os.environ['NAVER_CLIENT_ID']
CLIENT_SECRET = os.environ['NAVER_CLIENT_SECRET']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

def naver_shop_search(user_input: str) -> list:
    prompt = f"""
당신은 네이버 쇼핑에서 선물 추천을 위한 검색어 최적화 전문가입니다.

다음 문장은 사용자가 선물 추천을 요청한 상황입니다.
이 문장을 네이버 쇼핑에서 **실용적이고 감동적인 선물을 찾기 위한 핵심 검색어**로 바꿔주세요.

⚠️ 반드시 다음 조건을 지키세요:

- 검색어에는 다음 요소를 포함하세요 (가능한 경우):
    1. 수령인의 정체 (예: 어머니, 여자친구, 동료)
    2. 상황 또는 감정 (예: 생신, 감사, 축하, 응원)
    3. 선물의 성격 (예: 실용적인, 세련된, 센스있는)
- 5단어 이하의 간결한 **키워드 나열 형식**으로 출력하세요.
- 구체적이지만 일반 쇼핑 검색어로 적합해야 하며 문장이 되어서는 안 됩니다.

예시 입력: "어머니 생신을 축하드리기 위해 선물을 드리고 싶어요. 5만원 이하로 실용적인 아이템이면 좋겠어요."
예시 출력: 어머니 생신 선물 실용적인 5만원

입력: "{user_input}"
출력:
"""
    try:
        search_query = llm.invoke(prompt).content.strip()
    except Exception as e:
        print(f"[naver_tool] 쿼리 정제 중 오류: {e}")
        return []

    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    params = {
        "query": search_query,
        "display": 15,
        "start": 1,
        "sort": "sim"
    }

    url = "https://openapi.naver.com/v1/search/shop.json"
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
    except Exception as e:
        print(f"[naver_tool] 검색 API 오류: {e}")
        return []

    items = response.json().get("items", [])
    results = []
    for item in items:
        try:
            title = re.sub(r'<.*?>', '', item['title']).strip()
            price = int(item['lprice'])
            brand = item.get('brand', '브랜드 정보 없음')
            link = item['link']
            image = item['image']
            results.append({
                "BRAND": brand,
                "NAME": title,
                "PRICE": price,
                "IMAGE": image,
                "LINK": link
            })
        except Exception as e:
            print(f"[naver_tool] 항목 파싱 실패: {e}")
            continue

    return random.sample(results, min(len(results), 4))

naver_tool = Tool(
    name="naver_search",
    func=naver_shop_search,
    description="네이버 쇼핑에서 실시간으로 외부 상품을 검색합니다."
)

__all__ = ["naver_tool"]