from functools import partial
from langgraph.graph import StateGraph, END

from giftgraph.states import (
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
from giftgraph.agent import llm, create_agent

# agent_executor 생성
agent_executor = create_agent()

# LangGraph FSM
graph = StateGraph(state_schema=dict)

# FSM 각 단계 등록
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
graph.set_entry_point("ExtractSituation")

# 조건 분기
def situation_condition(state):
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

# FSM 빌드/컴파일
gift_fsm = graph.compile()
