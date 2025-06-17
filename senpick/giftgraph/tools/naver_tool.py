import os
import re
import requests
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from pathlib import Path
import random

base_path = Path(__file__).resolve().parent.parent
env_path = base_path / ".env"
load_dotenv(env_path)

CLIENT_ID = os.environ['NAVER_CLIENT_ID']
CLIENT_SECRET = os.environ['NAVER_CLIENT_SECRET']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=OPENAI_API_KEY
)

def naver_shop_search(user_input: str, recipient_info: dict = {}, situation_info: dict = {}) -> list:
    prompt = f"""
    당신은 네이버 쇼핑 검색 키워드 전문가입니다.

    사용자가 선물 추천을 요청했으며, 아래는 그 배경 정보입니다.
    이 정보를 바탕으로 네이버 쇼핑에 입력할 **간결하고 핵심적인 검색어 키워드**를 구성해 주세요.

    ⚠️ 반드시 아래 조건을 지키세요:
    - 수령인의 정보(성별, 나이대, 관계)가 반영되도록 하세요.
    - 키워드는 문장이 아닌 나열된 단어 형태로 구성하고, 최대 5단어 이내로 출력하세요.
    - 감사 카드, 편지지, 봉투, 택, 스티커와 같은 **단순 문구성 아이템은 최대 1개까지만 포함하도록 제한하세요.**
    - 가능한 경우, 실질적인 선물 유형(무드등, 뷰티, 소형가전 등)을 유도할 수 있는 키워드를 포함하세요.

    [입력 문장]
    {user_input}

    [상황 정보]
    감정: {situation_info.get('emotion', '')}
    스타일: {situation_info.get('preferred_style', '')}
    예산: {situation_info.get('price_range', '')}
    친밀도: {situation_info.get('closeness', '')}

    [수령인 정보]
    성별: {recipient_info.get('gender', '')}
    연령대: {recipient_info.get('ageGroup', '')}
    관계: {recipient_info.get('relation', '')}
    기념일/상황: {recipient_info.get('anniversary', '')}

    출력 (예시): 어머니 생신 선물 실용적인 5만원 이하
    """
    try:
        search_query = llm.invoke(prompt).content.strip()
    except Exception as e:
        print(f"[naver_tool] 코어 검색에서 오류: {e}")
        return []

    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET
    }

    params = {
        "query": search_query,
        "display": 30,
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
    if not items:
        return []
    
    # ✅ 중복 링크 제거
    unique_items = []
    seen_links = set()
    seen_names = set()
    for item in items:
        link = item.get("link")
        raw_title = item.get("title", "")
        title = re.sub(r'<.*?>', '', raw_title).strip()

        if not link or not title or link in seen_links or title in seen_names:
            continue

        seen_links.add(link)
        seen_names.add(title)
        unique_items.append(item)

    # ✅ 중복 제거된 것 중 무작위 4개 선택
    selected_items = random.sample(unique_items, min(4, len(unique_items)))

    results = []
    for item in selected_items:
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

    return results

naver_tool = Tool(
    name="naver_search",
    func=naver_shop_search,
    description="네이버 쇼핑에서 실시간으로 외부 상품을 검색합니다."
)

__all__ = ["naver_tool"]
