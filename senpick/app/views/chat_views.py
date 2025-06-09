from django.shortcuts import render
from django.http import JsonResponse

def chat(request):
    return render(request, 'chat.html')

def chat_history(request):
    chat_history = [
        {
            'id': 1,
            'title': "글자 몇개를 넣으면 좋을까요",
        },
        {
            'id': 2,
            'title': "공백 포함 11글자 가능하다",
        },
        {
            'id': 3,
            'title': "귀엽고 실용적인 친구 선물",
        },
        {
            'id': 4,
            'title': "귀엽고 실용적인 친구 선물 귀엽고 실용적인 친구 선물",
        },
        {
            'id': 5,
            'title': "귀엽고 실용적인 친구 선물 귀엽고 실용적인 친구 선물",
        },
        {
            'id': 6,
            'title': "귀엽고 실용적인 친구 선물 귀엽고 실용적인 친구 선물 귀엽고 실용적인 친구 선물",
        }
    ]      
    
    return JsonResponse({'chat_history': chat_history})