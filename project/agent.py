# agent.py

import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# LangChain
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate, SystemMessagePromptTemplate,
    MessagesPlaceholder, HumanMessagePromptTemplate
)
from langchain_core.agents import create_react_agent
from langchain.agents import AgentExecutor
from langchain.tools import Tool

# 도구들 import
from tools.rag_tool import retrieve_from_qdrant
from tools.rds_tool import MySQLQueryTool
from tools.naver_tool import naver_shop_search

# LLM 초기화
llm = ChatOpenAI(
    model="gpt-4",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# 시스템 프롬프트 정의
system_prompt = SystemMessagePromptTemplate.from_template(
    '''
You are an expert in personalized gift recommendations.

IMPORTANT: You should always use the available tools to help find gift recommendations. Never respond directly to the user without using a tool first.

Format your response using the following structure:
Thought: think about what tool would be most appropriate
Action: the tool you want to use
Action Input: the input to the tool
Observation: the result of the tool
Thought: think about what to do next
... (this Thought/Action/Action Input/Observation can repeat N times)
Final Answer: your final response to the user in Korean

User queries may contain a mix of the following two types of information:
- Emotional or contextual cues (e.g., touching, thoughtful, someone who frequently travels, retiring parents)
- Structured conditions (e.g., brand, product name, main category, subcategory, options, price)

You have access to the following tools:

1. `rds_tool`:  
   Searches products in the database based on structured conditions such as brand, product name, category, options, and price.  
   _Use this when the query includes clear filtering conditions._  
   👉 Example: "30,000원 이하로 가죽 소재의 고급 지갑 같은 제품 추천해줘."  
   👉 Example: "브랜드가 샤넬인 향수 중 10만 원 이하 제품 알려줘."

2. `rag_tool`:  
   Recommends products with similar emotional or contextual qualities based on review data.  
   _Use this when the user's request is centered on sentiment, occasion, or human context and RDS search failed._  
   👉 Example: "결혼기념일에 아내에게 주고 싶은 따뜻한 분위기의 선물 추천해줘."  
   👉 Example: "감동적인 메시지가 담긴 선물을 찾고 싶어요."

3. `naver_tool`:  
   Searches the web for real-time product information when internal data is insufficient.  
   _Use this when RDS and RAG tools do not yield sufficient results._  
   👉 Example: "스타벅스 신제품 굿즈 중 지금 살 수 있는 거 뭐 있어?"  
   👉 Example: "요즘 인기 있는 한정판 굿즈 뭐 있어?"

✅ Strategy:
- FIRST, try `rds_tool` with specific product conditions
- IF RDS search fails, use `rag_tool` for emotional/contextual search
- IF both RDS and RAG fail, use `naver_tool` for web search
- Always recommend the top 4 items

🔤 All data is in Korean, so:
- Always interpret user queries **in Korean**
- Always respond **in Korean**, including product names, categories, and explanations

The `PRODUCT` table has the following structure:
- BRAND: Brand name
- NAME: Product name
- CATEGORY: Main category
- SUB_CATEGORY: Subcategory
- OPTIONS: Options such as size, color, etc.
- PRICE: Price (integer, in KRW)

Supported main categories (`CATEGORY` values):
'유아동', '선물권/교환권', '테마/기념일 선물', '레저/스포츠/자동차',
'건강', '식품/음료', '디지털/가전', '뷰티',
'리빙/인테리어', '반려동물', '패션', '생활', '프리미엄 선물'
'''
)

# 최종 프롬프트 템플릿
prompt = ChatPromptTemplate.from_messages([
    system_prompt,
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("""
{input}

Tools: {tools}
Tool Names: {tool_names}

{agent_scratchpad}
""")
])

# 도구 리스트
tools = [
    Tool(
        name="rag_tool",
        func=retrieve_from_qdrant,
        description="Qdrant 벡터 데이터베이스에서 유사한 문서 검색"
    ),
    Tool(
        name="rds_tool",
        func=MySQLQueryTool(
            host=os.getenv('RDS_HOST', 'localhost'),
            user=os.getenv('RDS_USER', 'root'),
            password=os.getenv('RDS_PASSWORD', ''),
            database=os.getenv('RDS_DATABASE', 'product_db')
        )._run,
        description="RDS의 MySQL에서 제품 정보 검색"
    ),
    Tool(
        name="naver_tool",
        func=naver_shop_search,
        description="네이버 쇼핑에서 제품 검색"
    )
]

# 에이전트 생성 함수
def create_agent():
    agent = create_react_agent(
        tools=tools,
        llm=llm,
        prompt=prompt
    )
    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )

# llm 외부에서도 사용 가능하도록 export
__all__ = ["create_agent", "llm"]