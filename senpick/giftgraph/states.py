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

4가지 상황 정보("emotion", "preferred_style", "price_range", "closeness")를 채우기 위한 질문을 하세요.
4가지 상황 정보가 모두 있어야 추천이 가능합니다.
한 번에 한 정보만 질문하고, 한 정보는 최대 1회만 질문 가능합니다. 최대한 친근하고 자연스러운 말투로 질문하세요.

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
"closeness" : 친밀도 (가까움, 어색함, 친해지고 싶음, 애매함 등으로 요약)
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
최종 결정은 사용자에게 맡기고, 사용자 정보에 따른 비교 사유를 생성하는 데에 집중하세요. 

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
        for k in state["situation_info"]:
            if extracted.get(k):
                state["situation_info"][k] = extracted[k]
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

def call_agent(state, agent_executor: AgentExecutor = None) -> dict:
    history_str = "\n".join(state.get("chat_history", [])[-10:])
    try:
        user_intent = (
            f"[추출된 조건]\n감정: {state['situation_info'].get('emotion')}, \n"
            f"스타일: {state['situation_info'].get('preferred_style')}, \n"
            f"예산: {state['situation_info'].get('price_range')}원\n"
            f"친밀도: {state['situation_info'].get('closeness')}\n"
            f"[수령인 정보]\n{state.get('recipient_info', {})}\n"
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

        return {
            **state,
            "output": agent_response
        }

    except Exception as e:
        print(f"[call_agent 에러]: {e}")
        return {
            **state,
            "output": "추천 처리 중 에러가 발생했습니다."
        }

def final_response(state) -> dict:
    try:
        return {
            **state,
            "output": state.get("output")
        }
    except Exception as e:
        print(f"[final_response 에러]: {e}")
        return {
            **state,
            "output": "최종 응답 생성 중 에러가 발생했습니다."
        }

# ===================== 🔹 공통 출력 노드 (stream 기반) 🔹 =====================

# def stream_output(state, llm: ChatOpenAI, prompt_template):
#     try:
#         user_input = state["chat_history"][-1]
#         prompt = prompt_template.format(
#             user_input=user_input,
#             chat_history="\n".join(state.get("chat_history", [])[-10:]),
#             recipient_info=state.get("recipient_info", {}),
#             situation_info=state.get("situation_info", {})
#         )
#         output = ""
#         for chunk in llm.stream(prompt):
#             token = getattr(chunk, "content", "")
#             output += token
#             yield token  # 실시간 출력
#         yield {
#             **state,
#             "output": output
#         }
#     except Exception as e:
#         print(f"[stream_output 예외]: {e}")
#         yield {
#             **state,
#             "output": "출력 중 오류가 발생했습니다."
#         }

from langchain_core.messages import AIMessage

# def stream_output(state, llm: ChatOpenAI, prompt_template):
#     print("\n==== stream_output 진입 ====")
#     try:
#         chat_history = state.get("chat_history", [])
#         recipient_info = state.get("recipient_info", {})
#         situation_info = state.get("situation_info", {})

#         input_vars = set(prompt_template.input_variables)

#         if "user_input" in input_vars:
#             if not chat_history:
#                 raise ValueError("[stream_output] chat_history가 비어 있음")
#             user_input = chat_history[-1]
#             prompt = prompt_template.format(user_input=user_input)
#         else:
#             prompt = prompt_template.format(
#                 chat_history="\n".join(chat_history[-10:]),
#                 recipient_info=recipient_info,
#                 situation_info=situation_info
#             )

#         print("\n--- [LLM 전달 prompt] ---")
#         print(prompt)
#         print("-------------------------")

#         output = ""
#         for chunk in llm.stream(prompt):
#             token = getattr(chunk, "content", "")
#             output += token
#             yield AIMessage(content=token)  # ✅ 이렇게 하면 console에도 stream 출력됨

#         # 마지막에 상태 반환
#         yield {
#             **state,
#             "output": output,
#             "chat_history": chat_history + [output]
#         }

#     except Exception as e:
#         print(f"[stream_output 예외]: {e}")
#         yield {
#             **state,
#             "output": "출력 중 오류가 발생했습니다."
#         }
def stream_output(state, llm: ChatOpenAI, prompt_template):
    print("\n==== stream_output 진입 ====")
    try:
        chat_history = state.get("chat_history", [])
        recipient_info = state.get("recipient_info", {})
        situation_info = state.get("situation_info", {})

        input_vars = set(prompt_template.input_variables)

        if "user_input" in input_vars:
            if not chat_history:
                raise ValueError("[stream_output] chat_history가 비어 있음")
            user_input = chat_history[-1]
            prompt = prompt_template.format(user_input=user_input)
        else:
            prompt = prompt_template.format(
                chat_history="\n".join(chat_history[-10:]),
                recipient_info=recipient_info,
                situation_info=situation_info
            )


        output = ""
        for chunk in llm.stream(prompt):
            token = getattr(chunk, "content", "")
            output += token
            # ✅ 여기를 없애거나 로그로만 처리
            print(token, end="", flush=True)

        # 마지막에 상태 반환 (dict로!)
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
