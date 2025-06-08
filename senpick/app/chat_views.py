from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
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
        
        state = gift_fsm.invoke(state)
        save_state(request, state)
        return JsonResponse({"bot": state.get("output")})
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
            output = res

        save_state(request, state if isinstance(res, dict) else state)
        return JsonResponse({"bot": output})
    return JsonResponse({"error": "POST only"})
