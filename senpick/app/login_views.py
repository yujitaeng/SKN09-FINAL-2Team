from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from app.models.user import User 
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from django.views.decorators.csrf import csrf_exempt
from app.models.user import User
import json

def home(request):
    return render(request, 'login.html')

@csrf_exempt
def login_view(request):
    if request.method == "GET":
        return render(request, "login.html")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "email_error": "허용되지 않은 요청입니다."})

        email = data.get("username")
        password = data.get("password")

        if not email:
            return JsonResponse({"success": False, "email_error": "이메일을 입력해주세요."})
        if not password:
            return JsonResponse({"success": False, "password_error": "비밀번호를 입력해주세요."})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return JsonResponse({"success": False, "email_error": "이메일이 올바르지 않습니다."})

        if not check_password(password, user.password):
            return JsonResponse({"success": False, "password_error": "비밀번호가 올바르지 않습니다."})

        request.session["user_id"] = user.user_id
        request.session["nickname"] = user.nickname
        request.session["birth"] = user.birth
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "email_error": "잘못된 접근입니다."})

def logout_view(request):
    request.session.flush()  # 세션 초기화
    return redirect('login')  # 로그인 페이지로 리다이렉트
