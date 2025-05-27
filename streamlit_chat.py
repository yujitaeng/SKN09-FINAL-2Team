import streamlit as st
from datetime import datetime

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

# 상태 저장
if "liked_items" not in st.session_state:
    st.session_state.liked_items = set()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "show_favorites" not in st.session_state:
    st.session_state.show_favorites = False

# 챗봇 응답 함수
def get_bot_response(user_input):
    if "추천" in user_input:
        return {
            "type": "product",
            "products": [
                {"id": "p1", "title": "[센픽] 코롱 9ML 선물세트", "img": "https://via.placeholder.com/100", "link": "https://example.com/1"},
                {"id": "p2", "title": "[센픽] 뷰티 키트", "img": "https://via.placeholder.com/100", "link": "https://example.com/2"},
                {"id": "p3", "title": "[센픽] 건강식품 세트", "img": "https://via.placeholder.com/100", "link": "https://example.com/3"},
                {"id": "p4", "title": "[센픽] 디퓨저 선물", "img": "https://via.placeholder.com/100", "link": "https://example.com/4"},
            ]
        }
    else:
        return {
            "type": "text",
            "text": f"'{user_input}'에 대해 센픽이 추천을 도와드릴게요!"
        }

# 타이틀
st.title("🎁 센픽 챗봇")
st.markdown("어떤 선물이 필요하신가요?")

# 찜 목록 보기 토글 버튼
if st.button("❤️ 찜한 선물 보기" if not st.session_state.show_favorites else "❌ 찜 목록 닫기"):
    st.session_state.show_favorites = not st.session_state.show_favorites
    st.rerun()  # 토글 즉시 상태 반영

# 찜 목록 출력
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

# 채팅 출력
for msg, is_user, time in st.session_state.chat_history:
    role = "user" if is_user else "bot"

    with st.container():
        if isinstance(msg, str):
            st.markdown(
                f"<div class='chat-container'><div class='chat-message {role}'>{msg}</div><div class='timestamp {role}'>{time}</div></div>",
                unsafe_allow_html=True
            )
        elif isinstance(msg, dict) and msg.get("type") == "product":
            st.markdown(f"<div class='chat-container'><div class='chat-message bot'>🎁 추천 선물입니다!</div></div>", unsafe_allow_html=True)
            cols = st.columns(len(msg["products"]))
            for i, product in enumerate(msg["products"]):
                with cols[i]:
                    st.image(product["img"], use_container_width=True)
                    st.caption(product["title"])
                    st.markdown(f"[자세히 보기]({product['link']})", unsafe_allow_html=True)

                    # 좋아요 버튼 (토글 기능)
                    like_key = f"like_{product['id']}"
                    liked = product["id"] in st.session_state.liked_items
                    if st.button("💖 좋아요" if not liked else "✅ 찜 완료", key=like_key):
                        if liked:
                            st.session_state.liked_items.remove(product["id"])
                        else:
                            st.session_state.liked_items.add(product["id"])

            st.markdown(f"<div class='timestamp bot'>{time}</div>", unsafe_allow_html=True)

# 사용자 입력
user_input = st.chat_input("원하시는 선물 조건을 알려주세요!")
if user_input:
    now_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    st.session_state.chat_history.append((user_input, True, now_time))
    bot_response = get_bot_response(user_input)
    st.session_state.chat_history.append((bot_response, False, now_time))

    st.rerun()
