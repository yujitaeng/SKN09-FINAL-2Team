import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from app.models import User 
from app.utils import send_pswd_verification_code

def pswd(request):
    return render(request, 'pswd.html')

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

def pswd_verif(request):
    return render(request, 'pswd_verif.html')

@csrf_exempt
def resend_verification_code(request):
    try:
        _ = request.session.items()
        email = request.session.get("verification_email")

        if not email:
            return JsonResponse({"success": False, "message": "세션에 저장된 이메일이 없습니다."})

        send_pswd_verification_code(request, email)

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": f"재전송 실패: {str(e)}"})


@csrf_exempt
def verify_code(request):
    if request.method == "POST":
        data = json.loads(request.body)
        entered_code = data.get("code")

        if not entered_code:
            return JsonResponse({"success": False, "message": "인증번호를 입력해주세요."})

        saved_code = request.session.get("verification_code")
        if not saved_code:
            return JsonResponse({"success": False, "message": "세션이 만료되었거나 인증번호가 없습니다."})

        if entered_code != saved_code:
            return JsonResponse({"success": False, "message": "인증번호가 올바르지 않습니다."})

        return JsonResponse({"success": True})
    
    return JsonResponse({"success": False, "message": "잘못된 요청입니다."}, status=405)

def pswd_gen(request):
    return render(request, 'pswd_gen.html')

@csrf_exempt
def set_new_password(request):
    if request.method == "POST":
        data = json.loads(request.body)
        
        new_password = data.get("new_password", "").strip()
        email = request.session.get("verification_email")

        if not email:
            return JsonResponse({"success": False, "message": "세션 만료 또는 인증되지 않은 사용자입니다."})

        try:
            user = User.objects.get(email=email)

            if check_password(new_password, user.password):
                return JsonResponse({"success": False, "message": "이전 비밀번호입니다."})

            user.password = make_password(new_password)
            user.save()

            return JsonResponse({"success": True})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "해당 이메일의 사용자를 찾을 수 없습니다."})
    return JsonResponse({"success": False, "message": "잘못된 요청입니다."}, status=405)
