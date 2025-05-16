# agent.py

import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# LangChain
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate, SystemMessagePromptTemplate,
    MessagesPlaceholder, HumanMessagePromptTemplate
)
# from langchain_core.agents import create_react_agent
from langchain.agents import create_react_agent
from langchain.agents import AgentExecutor
from langchain.tools import Tool

# 도구들 import
from tools.rag_tool import retrieve_from_qdrant
from tools.rds_tool import MySQLQueryTool
from tools.naver_tool import naver_shop_search

# LLM 초기화
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# 시스템 프롬프트 정의
system_prompt = SystemMessagePromptTemplate.from_template(
    '''
You are an expert in personalized gift recommendations.

IMPORTANT RULES:
- You MUST use one of the available tools (`rds_tool`, `rag_tool`, `naver_tool`) to find product recommendations.
- NEVER provide the final answer directly without calling at least one tool.
- The user message may contain a mix of emotional cues (e.g., touching, thoughtful, practical) and structured data (e.g., price, category, brand).
- You must always follow the exact output format below.

TOOL STRATEGY:
1. First, try `rds_tool` if the user's message includes structured conditions (price, category, brand, etc.).
2. If RDS search fails or is insufficient, try `rag_tool` to find products based on emotion/context.
3. If both RDS and RAG yield poor results, use `naver_tool` to search the web in real time.

🚨 EXIT CONDITION:
- Once you have collected a total of **4 products** from any tool(s), you MUST stop searching and proceed to the Final Answer.
- DO NOT continue the Thought/Action loop after 4 products are ready.
- If a tool returns more than 4, select the most relevant ones.
- If multiple tools are used, combine the most appropriate results into exactly 4 items.

⚠️ GENERAL RULES:
- Never output Final Answer without at least one Observation.
- All Final Answer output MUST be in Korean.
- You MUST recommend exactly 4 items, even if you use multiple tools.
- DO NOT repeat or exceed 4 products.
- Each product in the Final Answer MUST include the following fields:
  1. 상품명 (Product Name)  
  2. 이미지 링크 (Image URL)  
  3. 상품 링크 (Product Link)  
  4. 가격 (Price, e.g., "₩72,000")  
  5. 간단한 설명 (Brief Description)

---

🧪 FEW-SHOT EXAMPLES:

Example 1:  
User: "감동적인 분위기의 결혼기념일 선물 추천해줘. 가격은 10만원 이하야."

Thought: 사용자의 감성적 요청과 함께 명확한 가격 조건이 있으므로 먼저 rds_tool로 검색해본다.  
Action: rds_tool  
Action Input: "CATEGORY: 테마/기념일 선물, PRICE <= 100000"  
Observation: 관련된 제품이 1개만 검색됨.  

Thought: 감동적인 분위기를 반영한 더 많은 추천을 위해 rag_tool을 사용한다.  
Action: rag_tool  
Action Input: "감동적인 분위기의 결혼기념일 선물 10만원 이하"  
Observation: 감성 기반 추천 상품 4개가 나왔다.  

Final Answer: 다음은 감동적인 결혼기념일에 어울리는 10만원 이하 선물 추천입니다:  
1.  
- **상품명**: 감성 캔들 세트  
- **가격**: ₩38,000  
- **이미지**: https://example.com/candle.jpg  
- **링크**: https://giftshop.com/candle  
- **설명**: 은은한 향으로 분위기를 더해주는 감성적인 캔들입니다.

2.  
- **상품명**: 커스텀 메시지 목걸이  
- **가격**: ₩55,000  
- **이미지**: https://example.com/necklace.jpg  
- **링크**: https://giftshop.com/necklace  
- **설명**: 감동적인 문구를 새길 수 있어 의미 있는 선물입니다.

3.  
- **상품명**: 드라이 플라워 박스  
- **가격**: ₩47,000  
- **이미지**: https://example.com/flowerbox.jpg  
- **링크**: https://giftshop.com/flowerbox  
- **설명**: 시들지 않는 꽃으로 추억을 오래 간직할 수 있습니다.

4.  
- **상품명**: 에세이 + 허브차 세트  
- **가격**: ₩32,000  
- **이미지**: https://example.com/booktea.jpg  
- **링크**: https://giftshop.com/booktea  
- **설명**: 감성적인 책과 향긋한 차의 조합으로 힐링을 선물하세요.

---

📌 ALWAYS FORMAT YOUR RESPONSE LIKE THIS:

Thought: (도구 선택의 이유 설명)  
Action: <tool_name>  
Action Input: <도구에 전달할 한국어 입력>  
Observation: <도구 결과 요약>  

(반복 가능)

Final Answer:  
- 반드시 한국어로 작성  
- 4개의 선물을 각 항목별로 아래 형식으로 제공:

1.  
- 상품명: ...  
- 가격: ...  
- 이미지: ...  
- 링크: ...  
- 설명: ...

(총 4개 제공)

---
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

# 에이전트 생성 함수
def create_agent():
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
        max_iterations=5,
        max_execution_time=9999,
    )

# llm 외부에서도 사용 가능하도록 export
__all__ = ["create_agent"]