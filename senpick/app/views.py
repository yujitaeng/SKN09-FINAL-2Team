from django.shortcuts import render
import os
import markdown
from django.conf import settings

def home(request):
    return render(request, 'index.html')

def login_view(request):
    return render(request, 'login.html')

def signup_step1(request):
    # return render(request, 'signup/signup_step1.html')

    base = os.path.join(settings.BASE_DIR, "app", "templates", "signup")
    # 서비스 이용약관
    with open(os.path.join(base, "service_term.txt"), encoding="utf-8") as f:
        md = f.read()
    service_html = markdown.markdown(md)
    # service_html = f.read() # 마크다운이 아니라 그냥 텍스트 파일 출력하려면 이 코드 사용
    # 개인정보 수집·이용 약관
    with open(os.path.join(base, "personal_term.txt"), encoding="utf-8") as f:
        md = f.read()
    personal_html = markdown.markdown(md)

    return render(request, "signup/signup_step1.html", {
        "service_content": service_html,
        "personal_content": personal_html,
    })

def signup_step2(request):
    return render(request, 'signup/signup_step2.html')

def signup_step3(request):
    return render(request, 'signup/signup_step3.html')

def signup_step4(request):
    return render(request, 'signup/signup_step4.html')

def signup_step5(request):
    return render(request, 'signup/signup_step5.html')