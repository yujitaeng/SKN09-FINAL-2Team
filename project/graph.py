# graph.py

from functools import partial
from langgraph.graph import StateGraph, END

from states import (
    handle_feedback,
    feedback_condition,
    extract_situation,
    ask_for_missing_info,
    conversation,
    call_agent,
    final_response,
    is_situation_complete,
    CONVERSATION_PROMPT,
    SITUATION_EXTRACTION_PROMPT
)
from agent import llm, create_agent

# agent_executor를 미리 생성
agent_executor = create_agent()

# LangGraph FSM, 상태는 dict만 쓴다!
graph = StateGraph(state_schema=dict)

# FSM 각 단계 등록 (partial로 리소스 주입)
graph.add_node(
    "ExtractSituation",
    partial(extract_situation, llm=llm, prompt_template=SITUATION_EXTRACTION_PROMPT)
)
graph.add_node(
    "AskQuestion", 
    partial(conversation, llm=llm, prompt_template=CONVERSATION_PROMPT)
)
graph.add_node(
    "AgentCall",
    partial(call_agent, agent_executor=agent_executor)
)
graph.add_node("Respond", final_response)
# graph.add_node("HandleFeedback", handle_feedback)
# 시작점 등록
graph.set_entry_point("ExtractSituation")


# 조건 분기 (상황 정보가 충분하면 AgentCall, 아니면 AskQuestion)
def situation_condition(state):
    # state는 dict임에 유의!
    if is_situation_complete(state["situation_info"], state["chat_history"]):
        return "complete"
    return "incomplete"

graph.add_conditional_edges(
    "ExtractSituation",
    situation_condition,
    {
        "complete": "AgentCall",
        "incomplete": "AskQuestion"
    }
)

# graph.add_conditional_edges(
#     "AgentCall",
#     feedback_condition,
#     {
#         "modify": "ExtractSituation",  # 상황 정보 수정 필요
#         "compare": "AskQuestion",       # 추가 질문 필요
#         # "end": END,                     # 대화 종료
#         # "ask_again": "HandleFeedback"   # 피드백 처리 후 다시 질문
#     }
# )

# graph.add_edge("Respond", "HandleFeedback")
# graph.add_conditional_edges(
#     "HandleFeedback",
#     feedback_condition,
#     {"modify": "ExtractSituation", "compare":"AskQuestion", "end": END, "ask_again": "HandleFeedback", }
# )

# 일반 상태 전이
# graph.add_edge("AskQuestion", "ExtractSituation")
# graph.add_edge("AgentCall", "Respond")
# graph.add_edge("Respond", "HandleFeedback")

# FSM 빌드/컴파일
gift_fsm = graph.compile()
