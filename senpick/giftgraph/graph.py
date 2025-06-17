# graph.py
from functools import partial
from langgraph.graph import StateGraph, END
from giftgraph.states import (
    extract_situation,
    call_agent,
    extract_action,

    CONVERSATION_PROMPT,
    SITUATION_EXTRACTION_PROMPT,
    ACTION_EXTRACTION_PROMPT,
    compare_prompt,
    refine_prompt,
    stream_output
)
from giftgraph.agent import llm, create_agent

# ✅ Agent 초기화
agent_executor = create_agent()

# ✅ FSM 초기화
graph = StateGraph(state_schema=dict)

# ✅ 노드 정의
graph.add_node(
    "ExtractSituation",
    partial(extract_situation, llm=llm, prompt_template=SITUATION_EXTRACTION_PROMPT)
)

graph.add_node(
    "ExtractAction", 
    partial(extract_action, llm=llm, prompt_template=ACTION_EXTRACTION_PROMPT)
)

# ✅ stream 기반 출력 노드들
graph.add_node(
    "AskQuestion",
    partial(stream_output, llm=llm, prompt_template=CONVERSATION_PROMPT)
)

graph.add_node(
    "Refine",
    partial(stream_output, llm=llm, prompt_template=refine_prompt)
)

graph.add_node(
    "Compare",
    partial(stream_output, llm=llm, prompt_template=compare_prompt)
)

graph.add_node(
    "AgentCall",
    partial(call_agent, agent_executor=agent_executor)
)

# ✅ 라우팅 노드: action에 따라 분기
def route_by_action(state):
    return state.get("action", "ask")

graph.add_node("RouteByAction", lambda state: state)  # 상태 변경 없음

# ✅ 흐름 정의
graph.set_entry_point("ExtractSituation")
graph.add_edge("ExtractSituation", "ExtractAction")
graph.add_edge("ExtractAction", "RouteByAction")

graph.add_conditional_edges("RouteByAction", route_by_action, {
    "ask": "AskQuestion",
    "recommend": "AgentCall",
    "compare": "Compare",
    "refine": "Refine"
})

# graph.add_edge("AskQuestion", "ExtractAction")

# ✅ FSM 빌드
gift_fsm = graph.compile()
