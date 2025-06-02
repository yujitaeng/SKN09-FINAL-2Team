from django.shortcuts import render, redirect
import os
import markdown
from django.conf import settings
import random
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

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

    if request.method == "GET":
        # 단순 GET: 약관 렌더링
        return render(request, "signup/signup_step1.html", {
            "service_content": service_html,
            "personal_content": personal_html,
        })

    # POST: 폼 데이터 수신 → 세션에 저장 후 Step2로 리디렉트
    elif request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()
        nickname = request.POST.get("nickname", "").strip()
        agree_terms = request.POST.getlist("agree")  # 필수 동의 체크박스

        # 1) 간단 검증 (예시: 이메일, 비밀번호, 닉네임이 빈 문자열인지)
        errors = {}
        if not email:
            errors["email"] = "이메일을 입력해주세요."
        # (추가: 이메일 정규식 검증 등)
        if not password:
            errors["password"] = "비밀번호를 입력해주세요."
        if not nickname:
            errors["nickname"] = "닉네임을 입력해주세요."
        # 필수 약관 두 개(agree) 모두 체크 여부
        if len(agree_terms) < 2:
            errors["terms"] = "필수 약관에 동의해주세요."

        if errors:
            # 에러가 있으면 GET과 동일하게 템플릿에 에러 메시지 전달
            return render(request, "signup/signup_step1.html", {
                "service_content": service_html,
                "personal_content": personal_html,
                "errors": errors,
                "email": email,
                "nickname": nickname,
                # (password는 보안상 재표시하지 않음)
            })

        # 2) 세션에 회원가입 기본정보 저장
        request.session["signup_email"] = email
        request.session["signup_password"] = password
        request.session["signup_nickname"] = nickname

        # 3) 인증 코드 생성 및 세션에 저장
        code = str(random.randint(10000, 99999))
        request.session["email_verification_code"] = code

        # 4) 이메일 발송 (Django send_mail 사용)
        subject = "[Senpick] 이메일 인증 코드 안내"
        message = f"Senpick 회원가입 인증 번호는 [{code}] 입니다.\n\n해당 번호를 인증번호 입력란에 입력해 주세요."
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            # 발송 실패 시, 다시 Step1으로 돌아가 에러 메시지 출력
            errors["email_send"] = "이메일 발송에 실패했습니다. 나중에 다시 시도해주세요."
            return render(request, "signup/signup_step1.html", {
                "service_content": service_html,
                "personal_content": personal_html,
                "errors": errors,
                "email": email,
                "nickname": nickname,
            })

        # 5) 발송 성공 → Step2로 이동
        return redirect("signup_step2")

def signup_step2(request):
    return render(request, 'signup/signup_step2.html')

def signup_step3(request):
    return render(request, 'signup/signup_step3.html')

def signup_step4(request):
    return render(request, 'signup/signup_step4.html')

def signup_step5(request):
    return render(request, 'signup/signup_step5.html')

@require_POST
def send_verification_code(request):
    email = request.session.get("signup_email")
    if not email:
        return JsonResponse({
            "success": False,
            "error": "세션에 이메일 정보가 없습니다. Step 1부터 다시 진행해주세요."
        }, status=400)

    # 5자리 랜덤 코드 생성
    code = str(random.randint(10000, 99999))
    request.session["email_verification_code"] = code

    subject = "[Senpick] 이메일 인증 코드 안내"
    message = f"Senpick 회원가입 인증 번호는 [{code}] 입니다.\n\n해당 번호를 인증번호 입력란에 입력해 주세요."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": "이메일 발송에 실패했습니다. 나중에 다시 시도해주세요."
        }, status=500)

    return JsonResponse({"success": True})

@csrf_exempt
@require_POST
def verify_code(request):
    code_input   = request.POST.get("code", "")
    stored_code  = request.session.get("email_verification_code")

    if not stored_code:
        return JsonResponse({
            "valid": False,
            "error": "인증코드가 존재하지 않습니다. 먼저 발송을 요청해주세요."
        }, status=400)

    if code_input == stored_code:
        # 검증 성공 시, 세션에서 인증 코드를 지워 보안 강화
        del request.session["email_verification_code"]
        return JsonResponse({"valid": True})
    else:
        return JsonResponse({"valid": False, "error": "인증번호가 일치하지 않습니다."}, status=200)