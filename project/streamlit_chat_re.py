from datetime import datetime
import json
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import (
    ChatPromptTemplate, HumanMessagePromptTemplate,
    MessagesPlaceholder, PromptTemplate
)
from langchain_core.messages import HumanMessage, AIMessage
import streamlit as st
from agents import create_agent
import time

# 채팅 모델 선언
chat_model = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-4o-mini",
)

# 시스템 프롬프트
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
    사용자 답변이 명확하지 않은 항목은 \"없다\", \"모름\" 등의 표현으로 채워도 됩니다.
    코드블럭 없이 JSON 형식으로 정확히 출력하세요.
"""
)

chat_chain = chat_prompt | chat_model
situation_info_chain = situation_info_prompt | chat_model

recipient_info = {
    'GENDER': "여성",
    'AGE_GROUP': "30대",
    'RELATION': "연인",
    'ANNIVERSARY': "100일",
}

situation_info = {
    "closeness": "",
    "emotion": "",
    "preferred_style": "",
    "price_range": ""
}

user_message = f"""
다음 정보를 바탕으로 기념일 선물을 추천해줘.
성별: {recipient_info['GENDER']}
연령대: {recipient_info['AGE_GROUP']}
관계: {recipient_info['RELATION']}
기념일 종류: {recipient_info['ANNIVERSARY']}
"""

def check_situation_info(info: dict) -> bool:
    return all(info.get(k) not in ["", "없다", "모름", "없음"] for k in ["emotion", "preferred_style", "price_range"])

def build_llm_chat_history():
    llm_chat_history = []
    for msg, is_user, _ in st.session_state.chat_history:
        if isinstance(msg, dict):
            content = msg.get("text", "")
        else:
            content = msg
        if is_user:
            llm_chat_history.append(HumanMessage(content=content))
        else:
            llm_chat_history.append(AIMessage(content=content))
    return llm_chat_history

def get_bot_response(user_input):
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    chat_history_for_llm = build_llm_chat_history()
    chat_history_for_llm.append(HumanMessage(content=user_input))
    res = chat_chain.invoke({
        "input": user_input,
        "chat_history": chat_history_for_llm
    })

    global situation_info
    situation_info_response = situation_info_chain.invoke({
        "chat_history": chat_history_for_llm,
        "current_info": json.dumps(situation_info)
    })
    situation_info = json.loads(situation_info_response.content)

    if check_situation_info(situation_info):
        agent = create_agent()
        agent_response = agent.invoke({
            "input": f"기념일 선물 추천을 위한 쿼리: {situation_info}",
            "chat_history": chat_history_for_llm
        })
        output_text = agent_response['output']
    else:
        output_text = res.content

    st.session_state.chat_history.append((output_text, False, now_time))
    return {"type": "text", "text": output_text}

# Streamlit 구성
st.set_page_config(page_title="센픽 GPT 채팅", layout="centered")

# CSS 스타일
st.markdown("""
    <style>
    .chat-container {
        display: flex;
        flex-direction: column;
        margin: 10px 0;
    }
    .chat-message {
        max-width: 70%;
        padding: 10px 15px;
        border-radius: 12px;
        margin-bottom: 2px;
        font-size: 0.95rem;
        line-height: 1.4;
        word-wrap: break-word;
        color: black !important;
    }
    .user {
        background-color: #DFFFD6;
        align-self: flex-end;
    }
    .bot {
        background-color: #F1F0F0;
        align-self: flex-start;
    }
    .timestamp {
        font-size: 0.7rem;
        color: #888;
        margin: 2px 4px;
        background-color: transparent !important;
    }
    .timestamp.user {
        text-align: right;
        align-self: flex-end;
    }
    .timestamp.bot {
        text-align: left;
        align-self: flex-start;
    }
    </style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    res = chat_chain.invoke({
        "input": user_message,
        "chat_history": st.session_state.chat_history
    })
    st.session_state.chat_history.append((res.content, False, datetime.now().strftime("%Y-%m-%d %H:%M")))
    
if "liked_items" not in st.session_state:
    st.session_state.liked_items = set()
if "show_favorites" not in st.session_state:
    st.session_state.show_favorites = False

st.title("🎁 센픽 챗봇")
st.markdown("어떤 선물이 필요하신가요?")

if st.button("❤️ 찜한 선물 보기" if not st.session_state.show_favorites else "❌ 찜 목록 닫기"):
    st.session_state.show_favorites = not st.session_state.show_favorites
    st.rerun()

if st.session_state.show_favorites:
    st.markdown("### ❤️ 찜한 선물 목록")
    liked_ids = st.session_state.liked_items
    all_products = {
        "p1": {"title": "[센픽] 코롱 9ML 선물세트", "img": "https://via.placeholder.com/100", "link": "https://example.com/1"},
        "p2": {"title": "[센픽] 뷰티 키트", "img": "https://via.placeholder.com/100", "link": "https://example.com/2"},
        "p3": {"title": "[센픽] 건강식품 세트", "img": "https://via.placeholder.com/100", "link": "https://example.com/3"},
        "p4": {"title": "[센픽] 디퓨저 선물", "img": "https://via.placeholder.com/100", "link": "https://example.com/4"},
    }
    liked_products = [all_products[pid] for pid in liked_ids if pid in all_products]
    if liked_products:
        cols = st.columns(len(liked_products))
        for i, product in enumerate(liked_products):
            with cols[i]:
                st.image(product["img"], use_container_width=True)
                st.caption(product["title"])
                st.markdown(f"[자세히 보기]({product['link']})", unsafe_allow_html=True)
    else:
        st.info("아직 찜한 선물이 없어요!")

for msg, is_user, timestamp in st.session_state.chat_history:
    role = "user" if is_user else "bot"
    with st.container():
        if isinstance(msg, str):
            st.markdown(f"<div class='chat-container'><div class='chat-message {role}'>{msg}</div><div class='timestamp {role}'>{timestamp}</div></div>", unsafe_allow_html=True)
        elif isinstance(msg, dict) and msg.get("type") == "product":
            st.markdown(f"<div class='chat-container'><div class='chat-message bot'>🎁 추천 선물입니다!</div></div>", unsafe_allow_html=True)
            cols = st.columns(len(msg["products"]))
            for i, product in enumerate(msg["products"]):
                with cols[i]:
                    st.image(product["img"], use_container_width=True)
                    st.caption(product["title"])
                    st.markdown(f"[자세히 보기]({product['link']})", unsafe_allow_html=True)
                    like_key = f"like_{product['id']}"
                    liked = product["id"] in st.session_state.liked_items
                    if st.button("💖 좋아요" if not liked else "✅ 찜 완료", key=like_key):
                        if liked:
                            st.session_state.liked_items.remove(product["id"])
                        else:
                            st.session_state.liked_items.add(product["id"])
            st.markdown(f"<div class='timestamp bot'>{time}</div>", unsafe_allow_html=True)

user_input = st.chat_input("원하시는 선물 조건을 알려주세요!")

if user_input:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.session_state.chat_history.append((user_input, True, timestamp))
    st.markdown(f"<div class='chat-container'><div class='chat-message user'>{user_input}</div><div class='timestamp user'>{timestamp}</div></div>", unsafe_allow_html=True)
    with st.spinner("🤖 봇이 생각 중입니다..."):
        bot_response = get_bot_response(user_input)
    st.rerun()