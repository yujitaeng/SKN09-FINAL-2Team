from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password
from app.models import User
from django.contrib.auth.hashers import check_password

def home(request):
    return render(request, 'pswd_gen.html')

@csrf_exempt
def set_new_password(request):
    if request.method == "POST":
        data = json.loads(request.body)
        # print("받은 데이터: ", data)
        new_password = data.get("new_password", "").strip()

        # print("받은 새 비밀번호:", new_password)

        email = request.session.get("verification_email")
        # print("세션 이메일:", email)

        if not email:
            return JsonResponse({"success": False, "message": "세션 만료 또는 인증되지 않은 사용자입니다."})

        try:
            user = User.objects.get(email=email)

            if check_password(new_password, user.password):
                return JsonResponse({"success": False, "message": "이전 비밀번호입니다."})

            user.password = make_password(new_password)
            user.save()
            # print("비밀번호 변경 성공")
            return JsonResponse({"success": True})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "message": "해당 이메일의 사용자를 찾을 수 없습니다."})
    return JsonResponse({"success": False, "message": "잘못된 요청입니다."}, status=405)
