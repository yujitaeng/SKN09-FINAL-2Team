from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, StreamingHttpResponse
import json
from giftgraph.graph import gift_fsm 

def chat(request):
    return render(request, 'chat.html')


def get_state(request):
    return request.session.get("chat_state", {
        "chat_history": [],
        "situation_info": {
            "closeness": "",
            "emotion": "",
            "preferred_style": "",
            "price_range": ""
        }
    })

def save_state(request, state):
    request.session["chat_state"] = state

@csrf_exempt
def chat_start(request):
    if request.method == "POST":
        data = json.loads(request.body)
       
        situation_info = {
            "closeness": ", ".join(data.get("who", [])),
            "emotion": ", ".join(data.get("emotion", [])),
            "preferred_style": ", ".join(data.get("style", [])),
            "price_range": ", ".join(data.get("budget", [])),
        }
        state = {
            "chat_history": [],
            "situation_info": situation_info
        }
        
        # # try:
        # situation_info = state.get("situation_info", {})
        # chat_str = "\n".join(state["chat_history"][-10:])
        # recipient_info = state.get("recipient_info", {})
        # prompt = prompt_template.format(
        #     chat_history=chat_str, 
        #     recipient_info=recipient_info, 
        #     situation_info=situation_info
        # )

        # for chunk in llm.stream(prompt):
        #     token = getattr(chunk, "content", "")
        #     yield token  # 실시간으로 토큰 출력
        
        # 스트림 처리 
        
        res = gift_fsm.invoke(state)
        
        if isinstance(res, dict):
            state = res
            output = state.get("output", "")
        else:  # 만약 res가 dict가 아니라면, 단순 문자열로 처리
            # 스트림 처리 
            def stream():
                for chunk in res:
                    yield chunk
    
            return StreamingHttpResponse(stream(), content_type='text/plain')
        save_state(request, state)
        return JsonResponse({"bot": output})
    return JsonResponse({"error": "POST only"})

@csrf_exempt
def chat_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        msg = data["message"]
        state = get_state(request)
        state["chat_history"].append(f"user: {msg}")

        res = gift_fsm.invoke(state)

        
        if isinstance(res, dict):
            state = res
            output = state.get("output", "")
        else:  
            def stream():
                for chunk in res:
                    yield chunk
    
            return StreamingHttpResponse(stream(), content_type='text/plain')

        save_state(request, state if isinstance(res, dict) else state)
        return JsonResponse({"bot": output})
    return JsonResponse({"error": "POST only"})
