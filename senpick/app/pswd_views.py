from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import User 
import random
import json
from django.http import JsonResponse

def home(request):
    return render(request, 'pswd.html')

def send_pswd_verification_code(request, email):
    code = ''.join([str(random.randint(0, 9)) for _ in range(5)])

    subject = "[Senpick] 비밀번호 찾기 인증 코드 안내"
    message = f"Senpick 비밀번호 찾기 인증 번호는 [{code}] 입니다.\n\n해당 번호를 인증번호 입력란에 입력해 주세요."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)

    request.session['verification_code'] = code
    request.session['verification_email'] = email
    request.session.set_expiry(500)
    request.session.modified = True
    
    print(code)

    return code


@csrf_exempt 
def password_reset_request(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email", "").strip()
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "잘못된 요청입니다."}, status=400)

        if not email:
            return JsonResponse({"success": False, "message": "이메일을 입력해주세요."}, status=400)

        if not User.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "존재하지 않는 이메일입니다."}, status=404)

        try:
            request.session['verification_email'] = email
            session_key = request.session.session_key

            response = JsonResponse({"success": True, "redirect_url": "/pswd/verif/"})
            response.set_cookie(
                key=settings.SESSION_COOKIE_NAME,
                value=session_key,
                max_age=None,
                expires=None,
                path='/',
                domain=None,                     
                secure=False,                    
                httponly=True,
                samesite='Lax'
            )
            return response
        except Exception as e:
            return JsonResponse({"success": False, "message": f"이메일 발송 실패: {str(e)}"}, status=500)
    return JsonResponse({"success": False, "message": "잘못된 요청입니다."}, status=405)