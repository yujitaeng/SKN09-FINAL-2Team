from django.shortcuts import render, redirect
import os
import markdown
import random
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from app.models import User, PreferType, UserPrefer
from django.contrib.auth.hashers import make_password

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

        # 2) DB 중복 검사: 이메일 혹은 닉네임이 이미 존재하는지
        if email:
            if User.objects.filter(email=email).exists():
                errors["email"] = "이미 사용 중인 이메일입니다."
        if nickname:
            if User.objects.filter(nickname=nickname).exists():
                errors["nickname"] = "이미 사용 중인 닉네임입니다."

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
        message = f"Senpick 회원가입 인증 번호는 [{code}] 입니다.\n\n해당 번호를 인증번호 입력란에 입력해 주세요.\n\n발신 전용 이메일입니다."
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

@require_GET
def check_duplicate(request):
    field = request.GET.get("field")
    value = request.GET.get("value", "").strip()
    if field not in ("email", "nickname"):
        return JsonResponse({"error": "invalid_field"}, status=400)
    if not value:
        return JsonResponse({"exists": False})

    # signup_step1과 똑같은 검사 로직
    exists = User.objects.filter(**{field: value}).exists()
    return JsonResponse({"exists": exists})

def signup_step2(request):
    return render(request, 'signup/signup_step2.html')

def signup_step3(request):
    if request.method == "GET":
        return render(request, "signup/signup_step3.html")

    # POST: 실제로 폼이 제출된 경우
    birth  = request.POST.get("birth", "").strip()
    gender = request.POST.get("gender", "").strip()
    job    = request.POST.get("job", "").strip()

    errors = {}
    if not birth or len(birth) != 8:
        errors["birth"] = "생년월일을 YYYYMMDD 형식으로 입력해주세요."
    if gender not in ("male", "female"):
        errors["gender"] = "성별을 선택해주세요."
    if not job:
        errors["job"] = "직업을 선택해주세요."

    # 검증 오류가 있으면 다시 Step3 폼 렌더
    if errors:
        return render(request, "signup/signup_step3.html", {
            "errors": errors,
            "birth": birth,
            "gender": gender,
            "job": job,
        })

    # 검증 통과: 세션에 저장 후 Step4로 이동
    request.session["signup_birth"]  = birth
    request.session["signup_gender"] = gender
    request.session["signup_job"]    = job
    return redirect("signup_step4")

def signup_step4(request):
    # ──────────────────────────────────────────────────────────────────────────────────
    # 1) GET 요청: 선호 옵션(스타일/카테고리)을 조회해서 템플릿에 넘김
    # ──────────────────────────────────────────────────────────────────────────────────
    if request.method == "GET":
        style_options    = PreferType.objects.filter(type="스타일")
        category_options = PreferType.objects.filter(type="카테고리")
        return render(request, "signup/signup_step4.html", {
            "style_options": style_options,
            "category_options": category_options,
        })

    # ──────────────────────────────────────────────────────────────────────────────────
    # 2) POST 요청: “회원가입 완료” 버튼 클릭 시
    #    (a) 세션에서 Step1/3 정보를 가져오고
    #    (b) POST로 넘어온 preference_ids를 파싱하여 UserPrefer 객체들을 생성하고
    #    (c) User 객체를 생성/저장 후 UserPrefer 저장 → Step5로 redirect
    # ──────────────────────────────────────────────────────────────────────────────────
    # (2-a) 세션에서 이전 단계(1,3)의 정보 꺼내기
    email    = request.session.get("signup_email")
    password = request.session.get("signup_password")
    nickname = request.session.get("signup_nickname")
    birth    = request.session.get("signup_birth")
    gender   = request.session.get("signup_gender")
    job      = request.session.get("signup_job")

    # 세션 정보가 하나라도 없으면, Step 1로 돌아가도록
    if not (email and password and nickname and birth and gender and job):
        return redirect("signup_step1")

    # (2-b) POST로 넘어온 “preference_ids” (예: "1,3,7,13,15")
    pref_ids_str = request.POST.get("preference_ids", "").strip()
    # 콤마로 분리 → 숫자로만 이루어진 ID 리스트
    pref_ids = [pid for pid in pref_ids_str.split(",") if pid.isdigit()]

    # (2-c) User 객체 생성 및 저장
    guest_user_id = request.session.get("user_id", None)  # 세션에 user_id가 있으면 가져옴

    user_qs = User.objects.filter(user_id=guest_user_id) if guest_user_id else None

    if user_qs and user_qs.exists():
        # 기존 guest user → 업데이트
        user = user_qs.first()
        user.email    = email
        user.password = make_password(password)
        user.nickname = nickname
        user.birth    = birth
        user.gender   = gender
        user.job      = job
        user.type     = "member"  # guest → member 전환
    else:
        # 새 user 생성 (guest_user_id 유지 필요)
        user = User(
            email=email,
            password=make_password(password),
            nickname=nickname,
            birth=birth,
            gender=gender,
            job=job,
            type="member",  # 명확하게 넣기
        )

    # 최종 저장
    user.save()

    # (2-e) 하나씩 UserPrefer 레코드 생성
    for pid in pref_ids:
        try:
            prefer_obj = PreferType.objects.get(prefer_id=int(pid))
        except PreferType.DoesNotExist:
            # 잘못된 ID면 무시
            continue

        UserPrefer.objects.create(
            user=user,
            prefer_type=prefer_obj
        )

    # (2-f) 세션 정리 (민감 정보 삭제)
    for key in [
        "signup_email", "signup_password", "signup_nickname",
        "signup_birth", "signup_gender", "signup_job"
    ]:
        if key in request.session:
            del request.session[key]

    # (2-g) 가입 완료 후 Step5로 리다이렉트
    return redirect("signup_step5")

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