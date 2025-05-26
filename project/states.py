import json, ast, re

SITUATION_EXTRACTION_PROMPT = """
다음은 사용자와 챗봇 간의 대화입니다:

{chat_history}

위 대화를 바탕으로 아래 항목들을 추론하세요.
- 오직 JSON 한 줄로만 출력
- 설명/줄바꿈/코드블럭 금지!
예시:
{{"closeness": "...", "emotion": "...", "preferred_style": "...", "price_range": "..."}}
정보가 불명확하면 "모름" 또는 "없다"로 채우세요.
JSON 외에는 아무것도 출력하지 마세요!
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
        prompt = prompt_template.format(chat_history=chat_str)
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
            "output": output
        }
    except Exception as e:
        print(f"[ask_for_missing_info 에러]: {e}")
        return {
            "chat_history": state.get("chat_history", []),
            "situation_info": state.get("situation_info", {}),
            "output": "추가 질문 생성 중 에러가 발생했습니다."
        }

def call_agent(state, agent_executor=None):
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
                stream_result += value
            agent_response = stream_result
        else:
            agent_response = "에이전트가 없습니다."
        
        return {
            "chat_history": state.get("chat_history", []),
            "situation_info": state.get("situation_info", {}),
            "output": agent_response
        }
    except Exception as e:
        print(f"[call_agent 에러]: {e}")
        return {
            "chat_history": state.get("chat_history", []),
            "situation_info": state.get("situation_info", {}),
            "output": "추천 처리 중 에러가 발생했습니다."
        }


def final_response(state) -> dict:
    try:
        return {
            "chat_history": state.get("chat_history", []),
            "situation_info": state.get("situation_info", {}),
            "output": state.get("output")
        }
    except Exception as e:
        print(f"[final_response 에러]: {e}")
        return {
            "chat_history": [],
            "situation_info": {},
            "output": "최종 응답 생성 중 에러가 발생했습니다."
        }
    
def handle_feedback(state):
    user_feedback = input("🤖: 추천 결과에 대해 어떻게 생각하시나요? (예: 더 저렴한, 다른 스타일, 다시 추천, 종료 등)\nuser: ").strip()
    state["chat_history"].append(f"user: {user_feedback}")
    state["user_feedback"] = user_feedback
    return state

def feedback_condition(state):
    fb = state.get("user_feedback", "").lower()
    if any(x in fb for x in ["다시", "변경", "더", "싫어", "아니", "없어", "재추천"]):
        return "modify"
    elif any(x in fb for x in ["마음에 들어", "좋아", "고마워", "종료", "끝"]):
        return "end"
    else:
        return "ask_again"

   # <-- 반드시 output key만 반환
