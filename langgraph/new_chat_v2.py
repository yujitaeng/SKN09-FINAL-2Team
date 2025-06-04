from datetime import datetime
import json, re
from typing import Optional, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.prompts import (
    ChatPromptTemplate, HumanMessagePromptTemplate,
    MessagesPlaceholder, PromptTemplate
)
from langchain_core.messages import HumanMessage, AIMessage
from agents import create_agent

# LLM 및 agent 초기화 (streaming 활성화)
chat_model = ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini", streaming=True)
agent = create_agent()

# 시스템 프롬프트
# system_message = """
# <시스템 프롬프트>
# 당신은 선물 추천 챗봇, '센픽'입니다.
# 당신의 역할은 다음과 같습니다. [대화(정보 질문), 선물 추천 agent 호출, 선물 비교, 입력확인] 

# [대화(정보 질문) - ask]
# 4가지 상황 정보("emotion", "preferred_style", "price_range", "closeness")를 채우기 위한 질문을 하세요.
# 4가지 상황 정보가 모두 있어야 추천이 가능합니다.
# 한 번에 한 정보만 질문하고, 한 정보는 최대 1회만 질문 가능합니다. 최대한 친근하고 자연스러운 말투로 질문하세요.
# - (주의) 사용자가 존재하지 않는 브랜드, 상품명에 대해 입력할 때에는 추천하지말고, 재확인 메시지를 출력하세요. 
# - 사용자가 모호한 표현을 사용했을 때에는 표현에 대해 재질문하세요.

# [선물 추천 agent 호출 - recommend]
# 상황 정보가 충분히 수집되었거나, 사용자가 추천을 요청하면 선물 추천 agent를 호출하세요.
# 사용자 선물 추천 요청 예시: 사용자가 명확히 "추천해줘", "찾아줘", "알려줘", "보고 싶어", "추천" 등의 의도를 밝힘
# 상황 정보가 이미 수집된 이후에는, 유사한 선물 요청("다른 분위기", "다른 스타일", "더 보고 싶어")도 recommend로 판단하세요.

# 직접 선물을 추천하거나 다른 말을 출력하지 마세요.

# [선물 비교 - compare]
# 사용자가 추천된 상품을 비교해달라고 요청하면 친절하게 비교 응답을 하세요. 
# (사용자 선물 비교 요청 예시:뭐가 더 좋은지 비교해줘/A랑 B 중에 뭐가 더 좋을 것 같아?/ ~를 생각하면 C가 더 좋겠지? 등)
# 최종 결정은 사용자에게 맡기고, 사용자 정보에 따른 비교 사유를 생성하는 데에 집중하세요. 

# [입력확인 - refine]
# refine은 ask보다 우선됩니다. 
# 사용자의 입력이 다음 중 하나에 해당할 경우 [ask]하지 말고 거절 메시지를 출력하세요.
# - 선물 추천과 무관한 응답, 질문
# - 존재하지 않는 브랜드나 잘못된 정보를 언급 (예: 센픽 전자 제품으로 찾아줘 등)
# - 과한 오타, 유행어, 은어, 뜻을 알 수 없거나 부정확한 표현이 포함된 경우 (예: 느좋 선물 추천해줘 등)
# 거절 메시지와 함께 사용자가 정보를 보완하거나 다시 입력할 수 있도록 친절하게 안내 + 질문을 함께 출력하세요.

# [주의]
# - 모든 출력은 항상 다음 형식을 따르세요:
# {{
#   "action": "ask" | "recommend" | "compare" | "refine",
#   "message": "실제 응답 텍스트"
# }}
# - 반드시 하나의 JSON 오브젝트만 출력하세요. JSON 뒤에는 아무 말도 하지 마세요.
# - 실제 추천은 당신이 하지 않고, 외부 시스템(agent)이 수행합니다. 직접 상품 이름이나 추천 문구를 출력하지 마세요.

# """

# 엄격하게 수정한 ver.
system_message = """
<시스템 프롬프트>
당신은 선물 추천 챗봇, '센픽'입니다.
당신의 역할은 다음과 같습니다. [대화(정보 질문), 선물 추천 agent 호출, 선물 비교, 입력확인] 

[대화(정보 질문) - ask]
4가지 상황 정보("emotion", "preferred_style", "price_range", "closeness")를 채우기 위한 질문을 하세요.
4가지 상황 정보가 모두 있어야 추천이 가능합니다.
한 번에 한 정보만 질문하고, 한 정보는 최대 1회만 질문 가능합니다. 최대한 친근하고 자연스러운 말투로 질문하세요.

[선물 추천 agent 호출 - recommend]
상황 정보가 충분히 수집되었거나, 사용자가 추천을 요청하면 선물 추천 agent를 호출하세요.
사용자 선물 추천 요청 예시: 사용자가 명확히 "추천해줘", "찾아줘", "알려줘", "보고 싶어", "추천" 등의 의도를 밝힘
단, 다음의 조건을 모두 만족해야 recommend로 판단하세요:
- 사용자의 요청이 구체적인 의도로 보일 것 (예: "다른 분위기의 선물 보고 싶어")
- 의미가 명확하며 실제 추천 의도로 판단 가능한 경우에만 recommend
- 모호하거나 의미가 불분명한 경우, 반드시 refine 처리
직접 선물을 추천하거나 다른 말을 출력하지 마세요.

[선물 비교 - compare]
사용자가 추천된 상품을 비교해달라고 요청하면 친절하게 비교 응답을 하세요. 
(사용자 선물 비교 요청 예시:뭐가 더 좋은지 비교해줘/A랑 B 중에 뭐가 더 좋을 것 같아?/ ~를 생각하면 C가 더 좋겠지? 등)
최종 결정은 사용자에게 맡기고, 사용자 정보에 따른 비교 사유를 생성하는 데에 집중하세요. 

[입력확인 - refine]
refine은 ask보다 우선됩니다. 
refine 액션은 사용자의 "입력 문장"만을 기준으로 판단하세요. situation_info의 내용이나 상태는 refine 여부에 영향을 주지 않습니다.
상황 정보가 채워진 이후라도, 사용자의 입력이 다음 중 하나에 해당할 경우 [ask]하지 말고 거절 메시지를 출력하세요.
- 선물 추천과 무관한 응답, 질문
- 존재하지 않는 브랜드나 잘못된 정보를 언급 (예: 센픽 전자 제품으로 찾아줘 등)
- 과한 오타, 유행어, 은어, 뜻을 알 수 없거나 부정확한 표현이 포함된 경우 (예: 느좋 선물 추천해줘 등)
거절 메시지와 함께 사용자가 정보를 보완하거나 다시 입력할 수 있도록 친절하게 안내 + 질문을 함께 출력하세요.

[주의]
- 모든 출력은 항상 다음 형식을 따르세요:
{{
  "action": "ask" | "recommend" | "compare" | "refine",
  "message": "실제 응답 텍스트"
}}
- 반드시 하나의 JSON 오브젝트만 출력하세요. JSON 뒤에는 아무 말도 하지 마세요.
- 실제 추천은 당신이 하지 않고, 외부 시스템(agent)이 수행합니다. 직접 상품 이름이나 추천 문구를 출력하지 마세요.

"""


# 프롬프트 설정
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    MessagesPlaceholder(variable_name="chat_history"),
    HumanMessagePromptTemplate.from_template("{input}"),
    HumanMessagePromptTemplate.from_template("현재까지 수집된 정보는 다음과 같습니다: {situation_info}")
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
)

situation_info_chain = situation_info_prompt | chat_model

chat_history = []

def check_situation_info(info: dict) -> bool:
    # return all(info.get(k) not in ["", "없다", "모름", "없음"] for k in ["emotion", "preferred_style", "price_range", "closeness"])
    return all(info.get(k) not in ["", "없다", "모름", "없음"] for k in ["emotion", "preferred_style", "price_range", "closeness"])

def extract_json_message(content: str) -> dict:
    try:
        first_brace = content.find('{')
        last_brace = content.rfind('}')
        if first_brace != -1 and last_brace != -1:
            json_part = content[first_brace:last_brace+1]
            obj = json.loads(json_part)
            if "action" in obj and "message" in obj:
                return obj
    except Exception as e:
        print(f"[extract_json_message 오류]: {e}")
    return {"action": "ask", "message": content.strip()}

def stream_llm_response(input_message, situation_info):
    formatted_messages = chat_prompt.format_messages(
        input=input_message,
        chat_history=chat_history,
        situation_info=situation_info
    )
    print("\n[LLM 응답]")
    response_text = ""
    for chunk in chat_model.stream(formatted_messages):
        token = getattr(chunk, "content", "")
        print(token, end="", flush=True)
        response_text += token
    print()
    return extract_json_message(response_text), response_text

# def chat(inputs: Optional[List[str]] = None):
def chat(inputs: Optional[List[str]] = None, recipient_info: Optional[dict] = None):
    if inputs is None:
        inputs = []
    if recipient_info is None:
        recipient_info = {
            'GENDER': "여성",
            'AGE_GROUP': "50대",
            'RELATION': "가족",
            'ANNIVERSARY': "감사·고마움",
        }
    chat_history = []
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

    chat_history.append(HumanMessage(content=user_message))

    situation_info_response = situation_info_chain.invoke({
        "chat_history": chat_history,
        "current_info": json.dumps(situation_info)
    })
    situation_info = json.loads(situation_info_response.content)

    parsed, full_response = stream_llm_response(user_message, situation_info)
    chat_history.append(AIMessage(content=full_response))

    for input_message in inputs:
        if input_message.strip().lower() == "exit":
            print("챗봇 종료")
            return


        print("\n[USER 입력]")
        print(input_message.strip())
        chat_history.append(HumanMessage(content=input_message))

        situation_info_response = situation_info_chain.invoke({
            "chat_history": chat_history,
            "current_info": json.dumps(situation_info)
        })
        situation_info = json.loads(situation_info_response.content)

        parsed, full_response = stream_llm_response(input_message, situation_info)
        chat_history.append(AIMessage(content=full_response))

        action = parsed.get("action", "ask")
        print("\n📌 [상황 정보 추론 결과]")
        print(json.dumps(situation_info, indent=2, ensure_ascii=False))
        print(f"[DEBUG] action: {action}")
        print(f"[DEBUG] situation valid: {check_situation_info(situation_info)}")

        if action == "recommend" and check_situation_info(situation_info):
            print("🎯 상황 정보가 모두 채워졌습니다. 에이전트에게 쿼리를 보냅니다...")
            agent_input = f"""
선물 추천을 위한 쿼리:

[수령인 정보]
- 성별: {recipient_info['GENDER']}
- 연령대: {recipient_info['AGE_GROUP']}
- 관계: {recipient_info['RELATION']}
- 상황: {recipient_info['ANNIVERSARY']}

[현재 상황 정보]
{json.dumps(situation_info, ensure_ascii=False)}
"""
            print("🔽 agent에 전달한 입력:")
            print(agent_input)
            agent_response = agent.invoke({
                "input": agent_input,
                "chat_history": chat_history
            })
            print("\n🎁 [추천 결과]")
            print(agent_response['output'])

    while True:
        input_message = input("사용자 입력 (종료: 'exit'): ")
        if input_message.lower() == 'exit':
            print("챗봇 종료.")
            break

        print("\n[USER 입력]")
        print(input_message.strip())
        chat_history.append(HumanMessage(content=input_message))

        situation_info_response = situation_info_chain.invoke({
            "chat_history": chat_history,
            "current_info": json.dumps(situation_info)
        })
        situation_info = json.loads(situation_info_response.content)

        parsed, full_response = stream_llm_response(input_message, situation_info)
        chat_history.append(AIMessage(content=full_response))

        action = parsed.get("action", "ask")
        print("\n📌 [상황 정보 추론 결과]")
        print(json.dumps(situation_info, indent=2, ensure_ascii=False))
        print(f"[DEBUG] action: {action}")
        print(f"[DEBUG] situation valid: {check_situation_info(situation_info)}")

        if action == "recommend" and check_situation_info(situation_info):
            print("🎯 상황 정보가 모두 채워졌습니다. 에이전트에게 쿼리를 보냅니다...")
            agent_input = f"""
선물 추천을 위한 쿼리:

[수령인 정보]
- 성별: {recipient_info['GENDER']}
- 연령대: {recipient_info['AGE_GROUP']}
- 관계: {recipient_info['RELATION']}
- 상황: {recipient_info['ANNIVERSARY']}

[현재 상황 정보]
{json.dumps(situation_info, ensure_ascii=False)}
"""
            print("🔽 agent에 전달한 입력:")
            print(agent_input)
            agent_response = agent.invoke({
                "input": agent_input,
                "chat_history": chat_history
            })
            print("\n🎁 [추천 결과]")
            print(agent_response['output'])
