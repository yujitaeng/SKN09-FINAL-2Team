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

# ✅ states.py 내 PromptTemplate 교체
CONVERSATION_PROMPT = PromptTemplate(
    input_variables=["chat_history", "recipient_info", "situation_info"],
    template="""
<시스템 프롬프트>
당신은 선물 추천 챗봇 '센픽'입니다. 

당신의 임무는 사용자의 수령인 정보(recipient_info)와 대화 내용을 바탕으로, 
'세부 상황', '감정', '예산', '스타일', '친밀도'를 자연스럽고 적절한 질문을 통해 유도하는 것입니다.

[세부 목표]
- 수령인 정보는 보통 '관계 / 성별 / 연령대 / 기념일' 수준이므로, 그 안에서 가능한 구체적 질문을 던져야 합니다.
- 예를 들어 '가족 / 여성 / 50대 / 생일' → 어머니, 시어머니, 장모님, 이모 중 누구인지 확인하는 질문 필요
- '연인 / 기념일'이라면 100일, 1주년, 프로포즈, 결혼기념일 중 어떤 의미인지 묻는 것이 적절
- '직장 동료 / 남성 / 40대 / 감사'라면 상사인지 동료인지 확인할 질문 필요
- 질문은 최대 4~5개까지만 던지며, 한 번 질문한 항목은 다시 묻지 않습니다.

[질문 예시 가이드 - 조건별 대응]
- 관계: '가족'이면 어떤 가족인지 / '지인'이면 어떤 관계인지 / '연인'이면 연애/결혼 상태 등
- 성별: 표현의 어투 조정
- 연령대: 10대 이하면 보호자, 50대 이상이면 존칭 등 반영
- 기념일/상황: 생일 외에도 감사, 명절, 축하, 사과, 승진 등 다양한 컨텍스트 파악 필요
- 관계가 '기타'일 경우 → 어떤 상황인지 자유롭게 묻기

[질문 스타일 규칙]
- 반드시 자연어 문장으로 출력하세요.
- 한 번에 하나의 정보만 질문하고, 동일한 항목에 대한 반복 질문은 하지 마세요.
- 질문은 최대 5개까지만 허용합니다.
- 너무 일반적인 질문은 피하고, 수령인 정보 기반으로 구체화하세요.
- 사용자와 실제 대화하듯 정중하면서 친근한 말투 사용
- 이모지는 한 문장당 1개 이하로 자연스럽게만 사용하세요.

[출력 형식 제한 사항 - 매우 중요]
- 마크다운 문법 기호(예: **굵게**, `- 리스트`, `# 제목`)는 절대 사용하지 마세요.
- HTML 태그(`<br>`, `<p>`, `<ul>` 등)도 절대 포함하지 마세요.
- 줄바꿈은 문단 단위 또는 자연스러운 흐름을 위해 1~2줄 간격만 사용하세요.
- 들여쓰기, 번호 매기기, 코드블록, 따옴표 인용 등의 구조는 사용하지 마세요.
- 전체 글은 실제 사람이 작성한 것처럼 자연스럽고 정돈된 문장 흐름을 유지하세요.
- 대신, 아래와 같은 자연어 문장 스타일로 출력하세요:
예시:
  제목처럼 보이게 하려면 → 줄바꿈 후 문장을 간결하게 시작하세요.
  강조하고 싶다면 → "특히", "가장 중요한 건", "꼭 기억해 주세요" 등등 같은 표현을 사용하세요.
  리스트처럼 보이게 하려면 → "1. ~", "2. ~" 또는 "첫째, ~ 둘째, ~" 식의 자연스러운 표현을 쓰세요.
  줄바꿈은 문단 단위로 1~2줄 간격만 사용하세요.

[사용자 입력 내역]
- 최근 대화 내용:
{chat_history}

- 현재 수령인 정보:
{recipient_info}

- 지금까지 파악된 상황 정보:
{situation_info}

출력: 위 내용을 바탕으로 지금 시점에서 부족한 상황정보를 채울수 있는 **가장 적절한 질문 하나만 자연스럽게 출력하세요.**
"""
)


# CONVERSATION_PROMPT = PromptTemplate(
#     input_variables=["chat_history", "recipient_info", "situation_info"],
#     template="""
# <시스템 프롬프트>
# 당신은 선물 추천 챗봇, '센픽'입니다.

# 당신의 목적은 사용자가 아직 제공하지 않은 상황 정보 중 하나를 자연스럽고 보기 좋은 질문으로 이끌어내는 것입니다.
# 상황 정보에는 다음이 포함됩니다: emotion, preferred_style, price_range, closeness

# [질문 작성 규칙]
# - 한 번에 하나의 정보만 질문합니다.
# - 동일한 정보는 두 번 이상 질문하지 않습니다.
# - 질문과 예시에는 반드시 줄바꿈 문자 \n 을 포함합니다.
#   예: "안녕하세요\n선물 추천을 도와드릴게요.\n먼저, ...\n예를 들면:\n- A\n- B\n..."
# - 이모지는 한 문장에 1개 이하로만 사용하며, 중복 없이 자연스럽게 배치합니다.
# - 텍스트 강조 시 마크다운 문법(**굵게**)은 절대 사용하지 않습니다.
# - 실제 마크다운 기호(\n, -, \\, **)나 HTML 태그(<br>)는 출력에 사용하지 않습니다.
#   오직 자연어 표현만 사용합니다.

# [closeness 주의]
# - closeness는 관계가 아니라 친밀도입니다. 관계를 다시 묻지 말고, "얼마나 가까운 느낌인지"를 묻는 질문을 구성하세요.
# - 예시는 다음과 같이 줄바꿈 문자로 출력하세요:
#   자주 연락하며 마음을 나누는 사이
#   일정한 거리감을 유지하는 사이
#   어색하지만 챙기고 싶은 사이
#   감사한 마음이 드는 사이

# [예시 질문 출력 형태]
# 아래와 같은 형식으로 출력하도록 유도하세요:
# 안녕하세요! 😊
# 선물 추천을 도와드릴게요.

# 먼저, 선물을 드릴 분과 얼마나 가까운 사이인지 알려주실 수 있을까요?<br>
# 예를 들어:
# - 자주 연락하며 마음을 나누는 사이
# - 일정한 거리감을 유지하는 사이
# - 어색하지만 챙기고 싶은 사이
# - 감사한 마음이 드는 사이

# 어떤 느낌에 가까우신가요?

# [입력으로 활용할 변수들]
# - 실제 추천은 당신이 하지 않고, 외부 시스템(agent)이 수행합니다. 직접 상품 이름이나 추천 문구를 출력하지 마세요.
# 다음은 사용자와 챗봇 간의 대화입니다:
# {chat_history}

# 현재 채워진 수령인 정보는 다음과 같습니다.
# {recipient_info}

# 채워야하는 상황 정보는 다음과 같습니다.
# {situation_info}
# """
# )

# ExtractSituation - extract_situation()
# 상황 정보 추출 
SITUATION_EXTRACTION_PROMPT = """
엄격한 정보 추출 가이드라인:
1. 대화 내용에 명시적으로 언급된 정보만 추출
2. 추론이나 임의 해석 금지
3. 언급되지 않은 필드는 빈 문자열로 유지

참고: 수령인 정보는 {recipient_info} 입니다.

대화 내용:
{chat_history}

현재 상황 정보:
{current_info}


사용자의 응답에서 다음과 같은 정보를 추론하여 추출하세요.
[추론해야 하는 정보]
"closeness" : 친밀도 수준 (가까움, 어색함, 예의상 등)
"emotion" : 감정 상태 또는 선물의 배경
"preferred_style" : 희망하는 선물 스타일
"price_range" : 예산 범위 (예: 3만원 이하, 5만원대 등)

[또한 아래 수령인 정보가 새로 명확해졌다면 기존 값을 덮어씌워 주세요:]
"relation" : 가족 → 어머니, 친구 → 동창 등
"ageGroup" : 20대, 50대 등
"gender" : 남성, 여성 등
"anniversary" : 생일, 승진, 집들이 등

[출력 형식]
JSON 딕셔너리 하나로 묶어서 출력하세요. 예:
{{
    "emotion": "감사",
    "preferred_style": "고급스러운",
    "relation": "어머니",
    "anniversary": "생신"
}}

[규칙]
- 정보 추론은 응답이 명확할 때에만 진행해야 합니다.
- 사용자 답변에 포함된 내용만 current_info에서 수정하여 출력합니다.
- 기존 정보보다 더 구체적인 표현이 있다면 반드시 덮어쓰기 하세요.
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

[출력 형식 제한 사항 - 매우 중요]
- 마크다운 문법 기호(예: **굵게**, `- 리스트`, `# 제목`)는 절대 사용하지 마세요.
- HTML 태그(`<br>`, `<p>`, `<ul>` 등)도 절대 포함하지 마세요.
- 줄바꿈은 문단 단위 또는 자연스러운 흐름을 위해 1~2줄 간격만 사용하세요.
- 들여쓰기, 번호 매기기, 코드블록, 따옴표 인용 등의 구조는 사용하지 마세요.
- 전체 글은 실제 사람이 작성한 것처럼 자연스럽고 정돈된 문장 흐름을 유지하세요.
- 대신, 아래와 같은 자연어 문장 스타일로 출력하세요:
예시:
  제목처럼 보이게 하려면 → 줄바꿈 후 문장을 간결하게 시작하세요.
  강조하고 싶다면 → "특히", "가장 중요한 건", "꼭 기억해 주세요" 등등 같은 표현을 사용하세요.
  리스트처럼 보이게 하려면 → "1. ~", "2. ~" 또는 "첫째, ~ 둘째, ~" 식의 자연스러운 표현을 쓰세요.
  줄바꿈은 문단 단위로 1~2줄 간격만 사용하세요.

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

[출력 형식 제한 사항 - 매우 중요]
- 마크다운 문법 기호(예: **굵게**, `- 리스트`, `# 제목`)는 절대 사용하지 마세요.
- HTML 태그(`<br>`, `<p>`, `<ul>` 등)도 절대 포함하지 마세요.
- 줄바꿈은 문단 단위 또는 자연스러운 흐름을 위해 1~2줄 간격만 사용하세요.
- 들여쓰기, 번호 매기기, 코드블록, 따옴표 인용 등의 구조는 사용하지 마세요.
- 전체 글은 실제 사람이 작성한 것처럼 자연스럽고 정돈된 문장 흐름을 유지하세요.
- 대신, 아래와 같은 자연어 문장 스타일로 출력하세요:
예시:
  제목처럼 보이게 하려면 → 줄바꿈 후 문장을 간결하게 시작하세요.
  강조하고 싶다면 → "특히", "가장 중요한 건", "꼭 기억해 주세요" 등등 같은 표현을 사용하세요.
  리스트처럼 보이게 하려면 → "1. ~", "2. ~" 또는 "첫째, ~ 둘째, ~" 식의 자연스러운 표현을 쓰세요.
  줄바꿈은 문단 단위로 1~2줄 간격만 사용하세요.

[참고]
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
        current_info = json.dumps(state["situation_info"], ensure_ascii=False)
        recipient_info = json.dumps(state.get("recipient_info", {}), ensure_ascii=False)

        prompt = prompt_template.format(
            chat_history=chat_str,
            current_info=current_info,
            recipient_info=recipient_info
        )

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

        # ✅ 상황 정보 업데이트
        for k in state["situation_info"]:
            if extracted.get(k):
                state["situation_info"][k] = extracted[k].strip()

        # ✅ 수령인 정보 업데이트 (덮어쓰기)
        recipient_keys = ["relation", "ageGroup", "gender", "anniversary"]
        if "recipient_info" not in state:
            state["recipient_info"] = {}

        for key in recipient_keys:
            if extracted.get(key):
                state["recipient_info"][key] = extracted[key].strip()

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

# def extract_titles_from_history(chat_history: list[str]) -> list[str]:
#     """chat_history에서 이전 추천된 상품명들만 추출"""
#     pattern = r'"NAME"\s*:\s*"([^"]+)"|- 상품명\s*:\s*(.*)'
#     titles = []
#     for msg in chat_history:
#         if msg.startswith("bot:"):
#             clean_msg = msg.replace('\\"', '"')  # 이스케이프 제거
#             matches = re.findall(pattern, clean_msg)
#             for match in matches:
#                 title = match[0] or match[1]
#                 if title:
#                     titles.append(title.strip())
#     return list(set(titles))[:10]

def call_agent(state: dict, agent_executor: AgentExecutor = None) -> dict:
    history_str = "\n".join(state.get("chat_history", [])[-10:])

    try:
        recipient_info = state.get("recipient_info", {})
        messager_analysis = state.get("messager_analysis", {})

        # ✅ 이전 추천 상품명 추출
        # previous_titles = extract_titles_from_history(state.get("chat_history", []))
        # previous_titles_str = ", ".join(previous_titles) if previous_titles else "없음"

        # ✅ 이전 상품까지 포함한 프롬프트 구성
        user_intent = (
            f"[추출된 조건]"
            f"- 감정: {state['situation_info'].get('emotion')}"
            f"- 스타일: {state['situation_info'].get('preferred_style')}"
            f"- 예산: {state['situation_info'].get('price_range')}원"
            f"- 친밀도: {state['situation_info'].get('closeness')}"
            f"[수령인 정보]"
            f"성별: {recipient_info.get('gender')}, "
            f"연령대: {recipient_info.get('ageGroup')}, "
            f"관계: {recipient_info.get('relation')}, "
            f"기념일/상황: {recipient_info.get('anniversary')}"
            f"[메시지 분석]"
            f"친밀도: {messager_analysis.get('intimacy_level', '알 수 없음')}, "
            f"감정 톤: {messager_analysis.get('emotional_tone', '알 수 없음')}, "
            f"성격: {messager_analysis.get('personality', '알 수 없음')}, "
            f"관심사: {messager_analysis.get('interests', '알 수 없음')}"
            # f"[이전 추천 상품]\n{previous_titles_str}\n"
            f"[대화 맥락]\n{history_str}"
        )

        stream_result = ""
        if agent_executor:
            for chunk in agent_executor.stream({
                "user_intent": user_intent,
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

def stream_output(state, llm: ChatOpenAI, prompt_template):
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

        output = ""
        for chunk in llm.stream(prompt):
            token = getattr(chunk, "content", "")
            output += token
            yield token

        print("[stream_output] 🔚 최종 상태 반환 직전")

    except Exception as e:
        print(f"[stream_output 예외]: {e}")
        yield f"오류 발생: {str(e)}"
