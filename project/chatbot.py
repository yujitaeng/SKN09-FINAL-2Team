import json
import ast
from langchain_openai import ChatOpenAI
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import ConversationChain, LLMChain
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import (
    ChatPromptTemplate, HumanMessagePromptTemplate,
    MessagesPlaceholder, PromptTemplate
)
from langchain.memory import ConversationBufferMemory
# from tools.rag_tool import vectorstore
from agent import create_agent

# ▶️ GPT 모델 초기화
chat_model = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-4o",
)

# ▶️ 대화 메모리
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
# retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

# ▶️ 초기 사용자 정보
recipient_info = {
    'GENDER': "여성",
    'AGE_GROUP': "30대",
    'RELATION': "연인",
    'ANNIVERSARY': "100일",
}

# ▶️ 상황 정보 초기 상태
situation_info = {
    "closeness": "",
    "emotion": "",
    "preferred_style": "",
    "price_range": ""
}
turn_count = 0

# ▶️ 견고한 JSON 파싱
def robust_json_extract(text):
    if '```' in text:
        text = text.split('```')[1].strip()
    try:
        return json.loads(text)
    except:
        try:
            return ast.literal_eval(text)
        except:
            return {}

# ▶️ 상황 정보 충족 조건
def is_situation_complete(info):
    required = ["closeness", "emotion", "preferred_style", "price_range"]
    return all(isinstance(info[k], str) and info[k].strip() for k in required)

# ▶️ 시스템 프롬프트 설정
system_message = """
<시스템 프롬프트>
당신은 간단한 이벤트용 선물을 추천해주는 챗봇입니다.
대화 초반에는 사용자에게 필요한 선물의 맥락을 물어보고, 구체적인 선물 제안은 하지 않습니다.

다음 항목 중 emotion, preferred_style, price_range 이 3가지가 모두 채워졌을 때만 추천을 시작하세요.
closeness는 선택 항목입니다.

그 전까지는 반드시 질문만 하며 정보를 유도하세요.
친근하고 자연스럽게 구어체로 질문해 주세요.
"""

chat_prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{input}")
])
# conversation = RunnableWithMessageHistory(
#     chat_model,
#     chat_prompt,
#     memory=memory
# )

conversation = ConversationChain(llm=chat_model, prompt=chat_prompt, memory=memory, verbose=False)
# ▶️ 상황 정보 추론 프롬프트
situation_info_prompt = PromptTemplate(
    input_variables=["chat_history", "current_info"],
    template="""
엄격한 정보 추출 가이드라인:
1. 대화 내용에 명시적으로 언급된 정보만 추출
2. 추론이나 임의 해석 금지
3. 언급되지 않은 필드는 빈 문자열로 유지

대화 내용:
{chat_history}

현재 상황 정보:
{current_info}

다음 항목을 추론하세요: 
사용자와 선물 받는 대상과의 친밀도: 질문을 통하지 않고 대화 내용을 통해 추론, 
선물하는 감정, 
선물 받는 사람의 선호, 
예산: 사용자가 명확하게 언급한 범위만 기록, 임의 추정 금지

나머지 내용은 최소 1번 이상 질문해야 합니다.
사용자 답변에 있는 내용만 current_info에서 수정하여 출력합니다.
사용자 답변이 명확하지 않은 항목은 "없다", "모름" 등의 표현으로 채워도 됩니다.
코드블럭 없이 JSON 형식으로 정확히 출력하세요.
"""
)

# situation_info_chain = chat_model.bind(tags=["situation_info"]).with_fallbacks([chat_model])
situation_info_chain = situation_info_prompt | chat_model

# ▶️ 검색 키워드 프롬프트
search_query_prompt = PromptTemplate(
    input_variables=["chat_history", "situation_info"],
    template="""
다음 대화 내용과 상황 정보를 참고하여, 검색 키워드를 한 문장으로 생성하세요.

[대화 내용]
{chat_history}

[상황 정보]
{situation_info}

→ 상황에 가장 적합한 상품을 검색할 수 있도록 핵심 키워드를 한 문장으로 출력해 주세요.
"""
)

# search_query_chain = LLMChain(llm=chat_model, prompt=search_query_prompt)
search_query_chain = search_query_prompt | chat_model

# ▶️ 추천 이유 프롬프트
recommend_prompt = PromptTemplate(
    input_variables=["query", "context"],
    template="""
[사용자 요청]
{query}

[추천 상품 목록]
{context}

위 정보를 바탕으로 따뜻하고 자연스럽게 추천 이유를 설명해주세요.
"""
)

# rag_response_chain = LLMChain(llm=chat_model, prompt=recommend_prompt)
# recommend_response_chain = recommend_prompt | chat_model

# ▶️ 상품 포맷
def format_products(docs):
    return "\n\n".join([
        f"상품명: {doc.metadata.get('title')}\n"
        f"브랜드: {doc.metadata.get('brand')}\n"
        f"가격: {doc.metadata.get('price')}\n"
        f"상품 링크: {doc.metadata.get('product_url')}"
        for doc in docs
    ])

# ▶️ 상황 정보 업데이트
def update_situation():
    chat_history_str = "\n".join([
        f"{msg.type}: {msg.content}" for msg in memory.chat_memory.messages
    ])
    result = situation_info_chain.invoke({
        "chat_history":chat_history_str,
        "current_info":json.dumps(situation_info, ensure_ascii=False)
    })
    updated = robust_json_extract(result.content)
    if updated:
        for k in situation_info:
            val = updated.get(k, "").strip()
            if val:
                situation_info[k] = val
    else:
        print("[⚠️ 상황 정보 파싱 실패] 응답 원문:", result)
    return chat_history_str

# ▶️ 응답 생성
def generate_response(user_input):
    global turn_count
    turn_count += 1

    print(f"[👤 사용자 입력]\n{user_input}\n")
    llm_response = conversation.invoke({"input":user_input})
    chat_history_str = update_situation()
    print(f"[📌 현재 상황 정보]\n{situation_info}")

    if turn_count >= 2:
        if is_situation_complete(situation_info):
            print("\n🎯 상황 정보가 완성되었습니다. 상품 추천을 시작합니다.")
            query = search_query_chain.invoke({
                "chat_history":chat_history_str,
                "situation_info":json.dumps(situation_info, ensure_ascii=False)
            }).content.strip()
            print(query)
            
            # 에이전트를 통한 검색 및 응답 생성
            agent_response = agent_executor.invoke({
                "input": f"{user_input}\n\n검색 키워드: {query}",
                "chat_history": memory.chat_memory.messages
            })
            if agent_response and 'output' in agent_response:
                return f"\n💬 에이전트 응답:\n{agent_response['output']}"
            else:
                return "적절한 추천을 찾지 못했습니다."
            # 에이전트 응답 처리
            # if agent_response and 'output' in agent_response:
            #     docs = retriever.invoke(f"query: {query}")
            #     context = format_products(docs)
            #     # reason = recommend_response_chain.invoke({"query":user_input, "context":context})
            #     return f"\n📦 추천 상품 목록:\n{context}\n\n💬 에이전트 응답:\n{agent_response['output']}"
            #     return f"\n📦 추천 상품 목록:\n{context}\n\n🎁 추천 이유:\n{reason}\n\n💬 에이전트 응답:\n{agent_response['output']}"
            # else:
            #     return "적절한 추천을 찾지 못했습니다."

    return f"\n[💬 챗봇 응답]\n{llm_response['response']}"

# ▶️ 실행 루프
def chat():
    print("🎁 챗봇을 시작합니다. 종료하려면 '종료'라고 입력하세요.\n")
    print(f"챗봇: {conversation.invoke({'input': f'user: {recipient_info}'})['response']}")

    while True:
        user_input = input("user: ")
        if user_input.strip().lower() == "종료":
            print("챗봇을 종료합니다.")
            break
        response = generate_response(user_input)
        print(response)

# 에이전트 초기화
agent_executor = create_agent()

# ▶️ 진입점
if __name__ == "__main__":
    chat()
