# states.py
import json, ast, re
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
from langchain.prompts import PromptTemplate

# ExtractAction - extract_aciton()
# aciton 추출 
ACTION_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["chat_history", "recipient_info", "situation_info"],
    template="""
<시스템 프롬프트>
당신은 선물 추천 챗봇 '센픽'의 판단 로직 역할을 맡고 있습니다.
당신의 유일한 임무는 사용자 입력을 분석하여 다음 중 어떤 목적(action)에 해당하는지를 판단하는 것입니다.
응답 메시지를 생성하지 마세요. 오직 "action" 하나만 결정하고 아래 JSON 형식으로 반환하세요.

[가능한 행동 유형 및 판단 기준]

[1. ask]
상황 정보(emotion, preferred_style, price_range, closeness)가 다 채워져있지 않을 때 `ask`로 판단하세요.

[2. recommend]
다음과 같은 경우에만 `recommend`로 판단합니다:
- 사용자가 명시적으로 선물을 "추천해달라", "찾아줘", "알려줘", "추천받고 싶다" 등의 의사를 밝힘
- 상황 정보가 어느 정도 채워져 있고, 요청이 모호하지 않음
→ 단, 의미가 불분명하거나 판단이 애매한 경우엔 `refine`으로 돌려야 합니다.

[3. compare]
추천된 여러 상품 중에서 사용자 요청이 "비교 판단"을 원하는 경우에 해당합니다.
예: "A랑 B 중에 뭐가 더 좋아?", "비교해줘", "어떤 게 더 낫지?" 등

[4. refine]
입력이 다음 중 하나에 해당하면 `refine`으로 처리하세요:
- 선물 추천과 무관한 질문
- 존재하지 않는 브랜드 언급 또는 시스템 외 요청
- 오타, 은어, 유행어, 의미 불명확한 표현 등
→ 이 경우 ask를 출력하지 말고 반드시 refine 처리로 지정하세요.

[출력 형식]
- 반드시 다음과 같은 JSON 형식으로 출력해야 합니다:
{{
  "action": "ask" | "recommend" | "compare" | "refine"
}}
- 다른 텍스트나 설명 없이 JSON 오브젝트 하나만 출력하세요.

[대화 내역]
{chat_history}

[수령인 정보]
{recipient_info}

[상황 정보]
{situation_info}
"""
)


# AskQuestion-conversation()
# 상황 정보 채우기 위한 질문 생성
# CONVERSATION_PROMPT = """
CONVERSATION_PROMPT = PromptTemplate(
    input_variables=["chat_history", "recipient_info", "situation_info"],
    template="""
<시스템 프롬프트>
당신은 선물 추천 챗봇, '센픽'입니다.

당신의 목적은 사용자가 아직 제공하지 않은 상황 정보 중 하나를 자연스럽고 보기 좋은 질문으로 이끌어내는 것입니다.
상황 정보에는 다음이 포함됩니다: emotion, preferred_style, price_range, closeness

[질문 작성 규칙]
- 한 번에 한 정보만 질문하고, 한 정보는 최대 1회만 질문 가능합니다.
- 질문과 예시 내용은 반드시 줄바꿈 문자 '<br>'을 포함하여 출력하세요.
  예: "안녕하세요<br>선물 추천을 도와드릴게요.<br>먼저, ...<br>예를 들면:<br>- A<br>- B<br>..."
- 이모지는 한 문장당 1개 이하, 반복되지 않게 자연스럽게 사용하세요.
- 텍스트 강조 시 마크다운 문법(예: **굵게**)은 절대 사용하지 마세요.
- 실제 마크다운 기호(\n, -, \, **), html 기호 (<br>)도 출력하지 마세요. 순수한 자연어로 구성할 것.
- 응답은 포맷 코드나 태그 없이 평문 자연어로만 구성하세요.

[closeness 주의]
- closeness는 관계가 아니라 친밀도입니다. 관계를 다시 묻지 말고, "얼마나 가까운 느낌인지"를 묻는 질문을 구성하세요.
- 예시는 다음과 같이 줄바꿈 문자로 출력하세요:
  자주 연락하며 마음을 나누는 사이<br>
  일정한 거리감을 유지하는 사이<br>
  어색하지만 챙기고 싶은 사이<br>
  감사한 마음이 드는 사이

[예시 질문 출력 형태]
아래와 같은 형식으로 출력하도록 유도하세요:
안녕하세요! 😊<br>
선물 추천을 도와드릴게요.<br>
<br>
먼저, 선물을 드릴 분과 얼마나 가까운 사이인지 알려주실 수 있을까요?<br>
예를 들어:<br>
- 자주 연락하며 마음을 나누는 사이<br>
- 일정한 거리감을 유지하는 사이<br>
- 어색하지만 챙기고 싶은 사이<br>
- 감사한 마음이 드는 사이<br>
<br>
어떤 느낌에 가까우신가요?

[입력으로 활용할 변수들]
- 실제 추천은 당신이 하지 않고, 외부 시스템(agent)이 수행합니다. 직접 상품 이름이나 추천 문구를 출력하지 마세요.
다음은 사용자와 챗봇 간의 대화입니다:
{chat_history}

현재 채워진 수령인 정보는 다음과 같습니다.
{recipient_info}

채워야하는 상황 정보는 다음과 같습니다.
{situation_info}
"""
)

# ExtractSituation - extract_situation()
# 상황 정보 추출 
SITUATION_EXTRACTION_PROMPT = """
엄격한 정보 추출 가이드라인:
1. 대화 내용에 명시적으로 언급된 정보만 추출
2. 추론이나 임의 해석 금지
3. 언급되지 않은 필드는 빈 문자열로 유지

대화 내용:
{chat_history}

현재 상황 정보:
{current_info}


사용자의 응답에서 다음과 같은 정보를 추론하여 추출하세요.
[추론해야하는 정보]
"closeness" : 친밀도 수준 (가까움, 어색함, 친해지고 싶음, 애매함 등으로 요약)
"emotion" : 선물의 동기나 배경이 된 감정 상태
"preferred_style" : 희망하는 선물의 스타일 (~한 느낌, ~한 스타일로 요약)
"price_range" : 예산 범위 (예: 상관 없음, 7만원대, 3만원 이하 등등)

[규칙]
- 정보 추론은 응답이 명확할 때에만 진행해야 합니다.
- 사용자 답변에 포함된 내용만 current_info에서 수정하여 출력합니다.
- 코드블럭 없이 JSON 형식으로 정확히 출력하세요.
"""


# Compare - compare_node()
# 비교 수행
compare_prompt = PromptTemplate(
    input_variables=["user_input", "chat_history", "situation_info", "recipient_info"],
    template="""
[선물 비교 - compare]
사용자가 추천된 상품을 비교해달라고 요청하면 친절하게 비교 응답을 하세요. 
(사용자 선물 비교 요청 예시: 뭐가 더 좋은지 비교해줘 / A랑 B 중에 뭐가 더 좋을 것 같아? / ~를 생각하면 C가 더 좋겠지? 등)

- 마크다운 문법은 절대 사용하지 마세요.
- 필요한 경우 줄바꿈을 활용해 가독성을 높이되, 전체 흐름은 문장형으로 자연스럽게 유지하세요.
- 이모지(✔️, 🎯 등)는 적절하게 활용해도 좋습니다.
- 객관적인 특징 비교와 함께, 사용자의 상황이나 감정을 고려한 설명을 넣어주세요.
- 결론을 단정적으로 내리지 말고, 선택은 사용자에게 맡기되, 방향을 제안하는 톤을 유지하세요.

예시:
데스크패드는 사무실 책상에서 바로 쓸 수 있어서 실용적이에요. 깔끔한 디자인 덕분에 전문적인 분위기를 줄 수 있고, 승진을 축하하는 의미로도 잘 어울려요.

반면, 타올은 좀 더 개인적인 느낌이 있어요. 집에서 자주 쓰는 실용적인 아이템이고, 부드럽고 고급스러운 분위기를 줄 수 있어서 예의 있는 선물로 좋아요.

실용성과 단정한 분위기를 원하신다면 데스크패드,
따뜻하고 정감 있는 느낌을 원하신다면 타올이 잘 맞을 거예요.
어느 쪽이 더 마음에 드세요?

[입력 내용]
{user_input}

[상황 정보]
{situation_info}

[수령인 정보]
{recipient_info}

[이전 대화 내역]
{chat_history}
"""
)


# Refine - refine_node()
# 거절 메시지, 재질문 등
refine_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="""
[입력확인 - refine]
refine은 ask보다 우선됩니다. 
refine 액션은 사용자의 "입력 문장"만을 기준으로 판단하세요. situation_info의 내용이나 상태는 refine 여부에 영향을 주지 않습니다.
상황 정보가 채워진 이후라도, 사용자의 입력이 다음 중 하나에 해당할 경우 [ask]하지 말고 거절 메시지를 출력하세요.
- 선물 추천과 무관한 응답, 질문
- 존재하지 않는 브랜드나 잘못된 정보를 언급 (예: 센픽 전자 제품으로 찾아줘 등)
- 과한 오타, 유행어, 은어, 뜻을 알 수 없거나 부정확한 표현이 포함된 경우 (예: 느좋 선물 추천해줘 등)

거절 메시지와 함께 사용자가 정보를 보완하거나 다시 입력할 수 있도록 친절하게 안내 + 질문을 함께 출력하세요.

단, 사용자가 "무난한 느낌, 고급스러운 느낌 등"과 같이 추상적인 표현으로 선물 추천을 요구할 때에는 refine 하지 말고 선물 추천을 진행하세요.
[입력 내용]
{user_input}
"""
)

# ===================== 🔹 공통 도구 🔹 =====================

def robust_json_extract(text: str):
    candidates = re.findall(r'```(?:json)?(.*?)```', text, re.DOTALL)
    if candidates:
        text = candidates[0].strip()
    match = re.search(r'\{.*\}', text.replace("\n", " "), re.DOTALL)
    if match:
        text = match.group()
    else:
        return {}
    try:
        result = json.loads(text)
        return result if isinstance(result, dict) else {}
    except Exception:
        try:
            result = ast.literal_eval(text)
            return result if isinstance(result, dict) else {}
        except Exception:
            return {}

# ===================== 🔹 상태 노드 함수들 🔹 =====================

def extract_situation(state, llm=None, prompt_template=None) -> dict:
    try:
        print("\n==== extract_situation 진입 ====")
        chat_str = "\n".join(state["chat_history"][-10:])
        current_info = "\n".join(f"{k}: {v}" for k, v in state["situation_info"].items())
        prompt = prompt_template.format(chat_history=chat_str, current_info=current_info)
        llm_response = llm.invoke(prompt)
        print("\n--- [LLM 응답 원문] ---")
        print(llm_response)
        llm_text = getattr(llm_response, "content", str(llm_response))
        print(f"[LLM 최종 텍스트 응답]: {llm_text}")
        extracted = robust_json_extract(llm_text)
        print("--- [파싱 결과] ---")
        print(extracted)
        print("-----------------------")
        if not isinstance(extracted, dict):
            print(f"[extract_situation] dict 아님! extracted={extracted}")
            extracted = {}
        if not extracted:
            print("⚠️ 추출된 정보 없음 — 기존 situation_info 유지")
            return state  # 아무 것도 수정하지 않고 종료
        for k in state["situation_info"]:
            if extracted.get(k):
                state["situation_info"][k] = extracted[k].strip()
        print("==== extract_situation 종료 ====\n")
        return state
    except Exception as e:
        print(f"[extract_situation 전체 예외]: {e}")
        return state

def extract_action(state, llm, prompt_template):
    try:
        chat_history = "\n".join(state.get("chat_history", [])[-10:])
        recipient_info = state.get("recipient_info", {})
        situation_info = state.get("situation_info", {})
        prompt = prompt_template.format(
            chat_history=chat_history,
            recipient_info=recipient_info,
            situation_info=situation_info,
        )
        response = llm.invoke(prompt)
        message = getattr(response, "content", "").strip()
        print("[ExtractAction LLM 응답]:")
        print(message)
        parsed = robust_json_extract(message)
        print("[Parsed JSON]:", parsed)
        if not isinstance(parsed, dict):
            print("[extract_action 경고] 올바르지 않은 JSON. 기본값 'ask'로 설정.")
            return {
                **state,
                "action": "ask",
                "output": "조금 더 구체적으로 말씀해 주실 수 있을까요?"
            }
        action = parsed.get("action", "ask")
        print(f"👉 결정된 action: {action}")
        return { **state, "action": action }
    except Exception as e:
        print("[extract_action 예외]:", e)
        return {
            **state,
            "action": "ask",
            "output": "죄송해요. 다시 한 번 입력해 주실 수 있을까요?"
        }

# def call_agent(state, agent_executor: AgentExecutor = None) -> dict:
#     history_str = "\n".join(state.get("chat_history", [])[-10:])
#     try:
#         user_intent = (
#             f"[추출된 조건]\n감정: {state['situation_info'].get('emotion')}, \n"
#             f"스타일: {state['situation_info'].get('preferred_style')}, \n"
#             f"예산: {state['situation_info'].get('price_range')}원\n"
#             f"친밀도: {state['situation_info'].get('closeness')}\n"
#             f"[수령인 정보]\n{state.get('recipient_info', {})}\n"
#             f"[대화 맥락]\n{history_str}"
#         )

#         stream_result = ""
#         if agent_executor:
#             for chunk in agent_executor.stream({
#                 "input": user_intent,
#                 "chat_history": state.get("chat_history", [])
#             }):
#                 value = chunk.get("output") if isinstance(chunk, dict) else str(chunk)
#                 if value:
#                     print(value, end="", flush=True)
#                     stream_result += value
#             agent_response = stream_result
#         else:
#             agent_response = "에이전트가 없습니다."

#         return {
#             **state,
#             "output": agent_response
#         }

#     except Exception as e:
#         print(f"[call_agent 에러]: {e}")
#         return {
#             **state,
#             "output": "추천 처리 중 에러가 발생했습니다."
#         }
import json

def call_agent(state, agent_executor: AgentExecutor = None) -> dict:
    history_str = "\n".join(state.get("chat_history", [])[-10:])
    try:
        recipient_info_str = (
            f"성별: {state['recipient_info'].get('gender')}, "
            f"연령대: {state['recipient_info'].get('age_range')}, "
            f"관계: {state['recipient_info'].get('relationship')}, "
            f"기념일/상황: {state['recipient_info'].get('occasion')}"
        )

        user_intent = (
            f"[추출된 조건]\n"
            f"- 감정: {state['situation_info'].get('emotion')}\n"
            f"- 스타일: {state['situation_info'].get('preferred_style')}\n"
            f"- 예산: {state['situation_info'].get('price_range')}원\n"
            f"- 친밀도: {state['situation_info'].get('closeness')}\n"
            f"[수령인 정보]\n{recipient_info_str}\n"
            f"[대화 맥락]\n{history_str}"
        )

        stream_result = ""
        if agent_executor:
            for chunk in agent_executor.stream({
                "input": user_intent,
                "chat_history": state.get("chat_history", [])
            }):
                value = chunk.get("output") if isinstance(chunk, dict) else str(chunk)
                if value:
                    print(value, end="", flush=True)
                    stream_result += value
            agent_response = stream_result
        else:
            agent_response = "에이전트가 없습니다."

        # ✅ JSON 문자열 파싱 시도 → observation에 저장
        try:
            observation = []
            if "Final Answer:" in agent_response:
                # Final Answer 이후 부분만 추출
                lines = agent_response.split("Final Answer:")[-1].strip().splitlines()

                if len(lines) >= 2:
                    # 안내 문구는 lines[0], JSON은 lines[1:]을 합쳐서 파싱
                    json_str = "\n".join(lines[1:])
                    parsed = json.loads(json_str)
                    if isinstance(parsed, list):
                        observation = parsed
            else:
                # Final Answer 없을 경우 전체 문자열을 시도
                parsed = json.loads(agent_response)
                if isinstance(parsed, list):
                    observation = parsed

        except Exception as e:
            print(f"[call_agent JSON 파싱 실패]: {e}")
            observation = []

        prev_urls = {
            p["product_url"]
            for p in state.get("recommended_products", [])
            if isinstance(p, dict) and "product_url" in p
        }

        # 🔹 중복 제거 (refresh 요청 시)
        if state.get("refresh_recommend"):
            observation = [
                p for p in observation
                if p.get("LINK") not in prev_urls and p.get("product_url") not in prev_urls
            ]
            state.pop("refresh_recommend", None)

        # 🔹 누적 저장
        existing_urls = {
            p["product_url"]
            for p in state.get("recommended_products", [])
            if isinstance(p, dict)
        }

        new_items = [
            {
                "product_url": p.get("LINK") or p.get("product_url", ""),
                "title": p.get("NAME") or p.get("title", "")
            }
            for p in observation
            if (p.get("LINK") or p.get("product_url", "")) not in existing_urls
        ]

        state.setdefault("recommended_products", []).extend(new_items)

        # 🔹 최종 상태 반환
        return {
            **state,
            "output": agent_response,
            "observation": observation
        }

    except Exception as e:
        print(f"[call_agent 에러]: {e}")
        return {
            **state,
            "output": "추천 처리 중 에러가 발생했습니다.",
            "observation": []
        }

def final_response(state):
    try:
        if isinstance(state, str):
            print("[⚠️ 경고] final_response에 문자열이 넘어옴. dict로 감쌈.")
            return {
                "chat_history": [],
                "situation_info": {},
                "recipient_info": {},
                "output": state  # 문자열 그대로 출력
            }

        return {
            **state,
            "output": state.get("output", "")
        }

    except Exception as e:
        print(f"[final_response 에러]: {e}")
        return {
            "chat_history": [],
            "situation_info": {},
            "recipient_info": {},
            "output": "최종 응답 생성 중 에러가 발생했습니다."
        }



def stream_output(state, llm: ChatOpenAI, prompt_template):
    print("\n==== stream_output 진입 ====")
    try:
        chat_history = state.get("chat_history", [])
        recipient_info = state.get("recipient_info", {})
        situation_info = state.get("situation_info", {})

        input_vars = set(prompt_template.input_variables)

        # ✅ input_variables에 따라 다르게 format 처리
        if {"user_input", "chat_history", "situation_info", "recipient_info"}.issubset(input_vars):
            if not chat_history:
                raise ValueError("[stream_output] chat_history가 비어 있음")
            user_input = chat_history[-1]
            prompt = prompt_template.format(
                user_input=user_input,
                chat_history="\n".join(chat_history[-10:]),
                recipient_info=recipient_info,
                situation_info=situation_info
            )
        elif {"user_input"}.issubset(input_vars):
            user_input = chat_history[-1] if chat_history else ""
            prompt = prompt_template.format(user_input=user_input)
        else:
            prompt = prompt_template.format(
                chat_history="\n".join(chat_history[-10:]),
                recipient_info=recipient_info,
                situation_info=situation_info
            )

        print("\n[stream_output] 📤 최종 prompt:\n", prompt)

        output = ""
        for chunk in llm.stream(prompt):
            token = getattr(chunk, "content", "")
            output += token
            yield token

        print("[stream_output] 🔚 최종 상태 반환 직전")
        yield {
            **state,
            "output": output,
            "chat_history": chat_history + [output]
        }

    except Exception as e:
        print(f"[stream_output 예외]: {e}")
        yield {
            **state,
            "output": "출력 중 오류가 발생했습니다."
        }
