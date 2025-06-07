from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from app.pswd_views import send_pswd_verification_code

def home(request):
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
