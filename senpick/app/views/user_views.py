
from django.http import JsonResponse
from django.shortcuts import render, redirect
from app.services.user_service import authenticate_user, initialize_user_session, AuthError, get_birth_recommendations

def home(request):
    return render(request, 'login.html')

def login_view(request):
    if request.method == "GET":
        return render(request, "login.html")

    if request.method == "POST":
        email = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not email:
            return render(request, "login.html", {"email_error": "이메일을 입력해주세요"})
        if not password:
            return render(request, "login.html", {"password_error": "비밀번호를 입력해 주세요."})

        try:
            user = authenticate_user(email, password)
            initialize_user_session(request, user)
            return redirect("chat")
        except AuthError as e:
            return render(request, "login.html", {"password_error": str(e)})

    return render(request, "login.html", {"password_error": "잘못된 접근입니다."})

def logout_view(request):
    request.session.flush()
    return redirect("login")

def birth(request):
    return render(request, 'birth.html')

def birth_recommend_products(request):
    user_id = request.session.get("user_id")
    current_year = int(request.session.get("current_year", 2025))

    products, error = get_birth_recommendations(user_id, current_year)
    
    if error:
        return JsonResponse({'error': error}, status=404)

    return JsonResponse({'products': products})
