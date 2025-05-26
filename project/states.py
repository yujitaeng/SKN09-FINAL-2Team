import json, ast, re
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor
CONVERSATION_PROMPT = """
<시스템 프롬프트>
당신은 선물 추천 챗봇, '센픽'입니다.
당신의 역할은 다음과 같습니다. [대화(정보 질문), 선물 추천 agent 호출, 선물 비교, 입력확인] 

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

def extract_situation(state, llm=None, prompt_template=None) -> dict:
    try:
        print("\n==== extract_situation 진입 ====")
        chat_str = "\n".join(state["chat_history"][-10:])
        current_info = "\n".join(state["situation_info"])
        prompt = prompt_template.format(chat_history=chat_str, current_info=current_info)
        llm_response = llm.invoke(prompt)
        print("\n--- [LLM 응답 원문] ---")
        print(llm_response)
        if hasattr(llm_response, "content"):
            llm_text = llm_response.content
        else:
            llm_text = str(llm_response)
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
        # 이 함수만 state 전체 반환 (FSM 흐름상 상황정보 누적 때문)
        return state
    except Exception as e:
        print(f"[extract_situation 전체 예외]: {e}")
        return state

def is_situation_complete(situation_info: dict) -> bool:
    required = ["emotion", "preferred_style", "price_range"]
    return all(isinstance(situation_info[k], str) and situation_info[k].strip() and situation_info[k] not in ["모름", "없다"] for k in required)

def ask_for_missing_info(state) -> dict:
    try:
        missing = [k for k, v in state["situation_info"].items() if not v.strip() or v in ["모름", "없다"]]
        ask_map = {
            "emotion": "어떤 감정이나 분위기의 선물을 원하시나요?",
            "preferred_style": "선호하는 스타일(예: 모던, 러블리, 심플 등)이 있으신가요?",
            "price_range": "예산을 알려주시면 더 정확하게 추천드릴 수 있어요."
        }
        question = " / ".join([ask_map[k] for k in missing if k in ask_map])
        output = question or "더 필요한 정보가 있다면 말씀해 주세요."
        return {
            "chat_history": state.get("chat_history", []),
            "situation_info": state.get("situation_info", {}),
            "recipient_info": state.get("recipient_info", {}),
            "output": output
        }
    except Exception as e:
        print(f"[ask_for_missing_info 에러]: {e}")
        return {
            "chat_history": state.get("chat_history", []),
            "situation_info": state.get("situation_info", {}),
            "recipient_info": state.get("recipient_info", {}),
            "output": "추가 질문 생성 중 에러가 발생했습니다."
        }
        
def conversation(state, llm:ChatOpenAI, prompt_template):
    # try:
    situation_info = state.get("situation_info", {})
    chat_str = "\n".join(state["chat_history"][-10:])
    recipient_info = state.get("recipient_info", {})
    prompt = prompt_template.format(
        chat_history=chat_str, 
        recipient_info=recipient_info, 
        situation_info=situation_info
    )

    for chunk in llm.stream(prompt):
        token = getattr(chunk, "content", "")
        yield token  # 실시간으로 토큰 출력

def call_agent(state, agent_executor:AgentExecutor=None) -> dict:
    history_str = "\n".join(state.get("chat_history", [])[-10:])
    try:
        user_intent = (
            f"[대화 맥락]\n{history_str}\n"
            f"[추출된 조건]\n감정: {state['situation_info'].get('emotion')}, "
            f"스타일: {state['situation_info'].get('preferred_style')}, "
            f"예산: {state['situation_info'].get('price_range')}원"
        )

        # 실시간 스트리밍 출력 받기
        stream_result = ""
        if agent_executor:
            for chunk in agent_executor.stream({
                "input": user_intent,
                "chat_history": state.get("chat_history", [])
            }):
                # chunk가 dict 타입일 수 있음
                if isinstance(chunk, dict):
                    value = chunk.get("output") or chunk.get("text") or str(chunk)
                else:
                    value = str(chunk)
                print(value, end="", flush=True)   # 콘솔에서 실시간으로 출력
                stream_result = value
            agent_response = stream_result
        else:
            agent_response = "에이전트가 없습니다."
        
        return {
            "chat_history": state.get("chat_history", []),
            "situation_info": state.get("situation_info", {}),
            "recipient_info": state.get("recipient_info", {}),
            "output": agent_response
        }
    except Exception as e:
        print(f"[call_agent 에러]: {e}")
        return {
            "chat_history": state.get("chat_history", []),
            "situation_info": state.get("situation_info", {}),
            "recipient_info": state.get("recipient_info", {}),
            "output": "추천 처리 중 에러가 발생했습니다."
        }


def final_response(state) -> dict:
    try:
        return {
            "chat_history": state.get("chat_history", []),
            "situation_info": state.get("situation_info", {}),
            "recipient_info": state.get("recipient_info", {}),
            "output": state.get("output")
        }
    except Exception as e:
        print(f"[final_response 에러]: {e}")
        return {
            "chat_history": [],
            "situation_info": {},
            "recipient_info": state.get("recipient_info", {}),
            "output": "최종 응답 생성 중 에러가 발생했습니다."
        }
    
def handle_feedback(state):
    user_feedback = input("🤖: 추천 결과에 대해 어떻게 생각하시나요? (예: 더 저렴한, 다른 스타일, 다시 추천, 종료 등)\nuser: ").strip()
    # TODO: 조건 초기화 로직 추가
    state["chat_history"].append(f"user: {user_feedback}")
    state["user_feedback"] = user_feedback
    return state

def feedback_condition(state):
    fb = state.get("user_feedback", "").lower()
    if any(x in fb for x in ["다시", "변경", "더", "싫어", "아니", "없어", "재추천"]):
        return "modify" # 재추천 => 다시 추천 진행
    elif any(x in fb for x in ["마음에 들어", "좋아", "고마워", "종료", "끝"]):
        return "end" # 채팅 종료
    else:
        return "ask_again" # 처음부터 다시 물어보기 => 조건 초기화

   # <-- 반드시 output key만 반환
