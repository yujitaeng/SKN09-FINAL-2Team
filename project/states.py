import json, ast, re

# SITUATION_EXTRACTION_PROMPT = """
# 아래 항목을 반드시 오직 JSON 한 줄로만 출력하세요.
# - 코드블럭, 설명, 줄바꿈, 따옴표 감싸기, 추가 텍스트 모두 금지!
# 예시:
# {"closeness": "...", "emotion": "...", "preferred_style": "...", "price_range": "..."}
# 정보가 불명확하면 "모름" 또는 "없다"로 채우세요.
# JSON 외에는 아무것도 출력하지 마세요!
# """
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
    import json, ast, re
    # 코드블럭 안만 추출
    candidates = re.findall(r'```(?:json)?(.*?)```', text, re.DOTALL)
    if candidates:
        text = candidates[0].strip()
    # 한 줄 JSON만 추출 (여러 줄 있으면 무시)
    match = re.search(r'\{.*\}', text.replace("\n", " "), re.DOTALL)
    if match:
        text = match.group()
    else:
        return {}
    try:
        result = json.loads(text)
        if isinstance(result, dict):
            return result
        else:
            return {}
    except Exception:
        try:
            result = ast.literal_eval(text)
            if isinstance(result, dict):
                return result
            else:
                return {}
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

        # LLM 응답에서 실제 텍스트만 추출
        if hasattr(llm_response, "content"):
            llm_text = llm_response.content
        else:
            llm_text = str(llm_response)  # fallback

        print(f"[LLM 최종 텍스트 응답]: {llm_text}")
            
        # JSON 파싱 시도
        extracted = robust_json_extract(llm_text)
        # extracted = robust_json_extract(llm_response)
        print("--- [파싱 결과] ---")
        print(extracted)
        print("-----------------------")
        # 💡 for문 전에 robust하게 dict만 허용
        if not isinstance(extracted, dict):
            print(f"[extract_situation] dict 아님! extracted={extracted}")
            extracted = {}
        # 여기서부터는 dict일 때만 동작
        for k in state["situation_info"]:
            if extracted.get(k):
                state["situation_info"][k] = extracted[k]
        print("==== extract_situation 종료 ====\n")
        return state
    except Exception as e:
        print(f"[extract_situation 전체 예외]: {e}")
        return state



def is_situation_complete(situation_info: dict) -> bool:
    required = ["emotion", "preferred_style", "price_range"]
    return all(isinstance(situation_info[k], str) and situation_info[k].strip() and situation_info[k] not in ["모름", "없다"] for k in required)

def ask_for_missing_info(state) -> dict:
    missing = [k for k, v in state["situation_info"].items() if not v.strip() or v in ["모름", "없다"]]
    ask_map = {
        "emotion": "어떤 감정이나 분위기의 선물을 원하시나요?",
        "preferred_style": "선호하는 스타일(예: 모던, 러블리, 심플 등)이 있으신가요?",
        "price_range": "예산을 알려주시면 더 정확하게 추천드릴 수 있어요."
    }
    question = " / ".join([ask_map[k] for k in missing if k in ask_map])
    state["output"] = question or "더 필요한 정보가 있다면 말씀해 주세요."
    return state

def call_agent(state, agent_executor=None) -> dict:
    user_intent = (
        f"감정: {state['situation_info']['emotion']}, "
        f"스타일: {state['situation_info']['preferred_style']}, "
        f"예산: {state['situation_info']['price_range']}원"
    )
    agent_response = agent_executor.run(user_intent) if agent_executor else "에이전트가 없습니다."
    state["output"] = agent_response
    return state

def final_response(state) -> dict:
    return state
