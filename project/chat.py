from graph import gift_fsm
import traceback
def print_chat_history(state):
    try:
        print("\n[대화 기록]")
        for msg in state.get("chat_history", [])[-6:]:
            print(msg)
        print("--------------")
    except Exception as e:
        print(f"[print_chat_history 에러]: {e}")

def run_chatbot():
    print("🎁 선물 추천 챗봇 Senpick에 오신 걸 환영합니다!")
    print("챗봇과 대화를 시작하세요. (종료하려면 '종료' 입력)")
    print("-" * 40)

    state = {
        "chat_history": [],
        "situation_info": {
            "closeness": "",
            "emotion": "",
            "preferred_style": "",
            "price_range": ""
        },
        "output": None,
        "loop_count": 0
    }
    first_turn = True

    while True:
        try:
            if first_turn:
                greeting = "안녕하세요! 어떤 상황이나 감정에 맞는 선물을 찾고 계신가요? (예: 감사, 기념일, 취업 등)"
                print(f"\n🤖: {greeting}\n")
                state["chat_history"].append(f"bot: {greeting}")
                first_turn = False

            user_input = input("user: ").strip()
            if user_input.lower() in ["종료", "exit", "quit"]:
                print("챗봇을 종료합니다. 좋은 하루 되세요!")
                break

            state["chat_history"].append(f"user: {user_input}")

            try:
                state = gift_fsm.invoke(state)
            except Exception as e:
                print("\n⚠️ [gift_fsm.invoke] 에러:", str(e))
                traceback.print_exc()
                continue

            if state.get("output"):
                print(f"\n🤖: {state['output']}\n")
                state["chat_history"].append(f"bot: {state['output']}")

            state["loop_count"] = state.get("loop_count", 0) + 1
            if state["loop_count"] > 5:
                print("\n🤖: 정보 추출에 반복적으로 실패했습니다. 더 구체적으로 입력해 주세요!")
                break

            if state.get("output") and (
                "추천드리는 상품 목록" in state["output"] or
                "아래 상품들을 추천드립니다" in state["output"]
            ):
                print("챗봇이 추천을 완료했습니다. 대화를 종료합니다.")
                break
        except Exception as e:
            print(f"[run_chatbot 전체 에러]: {e}")

if __name__ == "__main__":
    run_chatbot()
