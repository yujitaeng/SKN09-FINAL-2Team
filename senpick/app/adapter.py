from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from .models import User
import uuid
import pprint
import secrets

# ✅ 디버깅용 함수 (클래스 바깥)
def social_debug_hook(request, sociallogin, **kwargs):
    print("=== [DEBUG: social_debug_hook 호출됨] ===")
    print("소셜 로그인 provider:", sociallogin.account.provider)
    print("sociallogin.user =", sociallogin.user)
    print("sociallogin.account =", pprint.pformat(sociallogin.account.extra_data))
    print("=== [END DEBUG] ===")

class MySocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        pprint.pprint(sociallogin.account.extra_data)
        provider = sociallogin.account.provider
        extra_data = sociallogin.account.extra_data

        # 이메일 추출
        email = ""
        if provider == "naver":
            email = extra_data.get("email", "")
        elif provider == "google":
            email = extra_data.get("email", "")
        elif provider == "kakao":
            email = extra_data.get("email", "")

        email = extra_data.get("email", "").strip().lower()
        print(f"📩 추출된 이메일: '{email}'")
        existing_user = User.objects.filter(email=email).first()
        if not email:
            print("❌ [PRE_SOCIAL_LOGIN] 이메일 없음 → 차단")
            raise ImmediateHttpResponse(redirect("/login/?error=email_required"))
        print(existing_user)
        if existing_user:
            print("🔁 기존 유저 연결")
            sociallogin.connect(request, existing_user)
            sociallogin.account.user = existing_user
            # if provider == "google":
            #     if not existing_user.birth or not existing_user.gender:
            #         print("➡️ 구글: step3으로 이동 (추가 정보 필요)")
            #         raise ImmediateHttpResponse(redirect("/signup/step3/"))
            #     elif not existing_user.is_email_verified:
            #         print("➡️ 구글: step4으로 이동 (선호 정보 입력)")
            #         raise ImmediateHttpResponse(redirect("/signup/step4/"))
            #     else:
            #         print("➡️ 구글: 가입 완료 → chat 이동")
            #         raise ImmediateHttpResponse(redirect("/chat"))

            # else:  # 네이버
            #     if not existing_user.is_email_verified:
            #         print("➡️ step4으로 이동 (가입 미완료)")
            #         raise ImmediateHttpResponse(redirect("/signup/step4/"))
            #     else:
            #         print("➡️ chat으로 이동 (가입 완료)")
            #         raise ImmediateHttpResponse(redirect("/chat"))

    def save_user(self, request, sociallogin, form=None):
        print("🔥 [SAVE_USER] 진입")
        user = sociallogin.user
        provider = sociallogin.account.provider
        extra_data = sociallogin.account.extra_data

        print(f"🌐 [SAVE_USER] provider = {provider}")
        print(f"📦 [SAVE_USER] extra_data = {extra_data}")

        email = nickname = birth = gender = profile_image = ""

        if provider == "naver":
            data = extra_data.get("response", {})
            email = extra_data.get("email", "")
            nickname = extra_data.get("nickname", "")
            profile_image = data.get("profile_image", "")
            gender = extra_data.get("gender", "")
            birthyear = extra_data.get("birthyear", "")
            birthday = extra_data.get("birthday", "").replace("-", "")
            if birthyear and birthday:
                birth = birthyear + birthday

        elif provider == "google":
            email = extra_data.get("email", "")
            nickname = extra_data.get("name", "구글사용자")
            profile_image = extra_data.get("picture", "")
        
        # 네이버 입력 변환
        if gender == "M":
            gender = "male"
        elif gender == "F":
            gender = "female"

        user.user_id = uuid.uuid4().hex
        user.email = email.strip().lower()
        user.nickname = nickname
        user.password = secrets.token_hex(16)
        user.type = "social"
        user.social_provider = provider
        user.is_email_verified = False
        user.birth = birth
        user.gender = gender
        user.job = ''
        user.profile_image = profile_image
        print("💾 저장 직전 값 확인:")
        print(f"  email = {user.email}")
        print(f"  nickname = {user.nickname}")
        print(f"  birth = {user.birth}")
        print(f"  gender = {user.gender}")

        user.save()

        sociallogin.user = user
        sociallogin.account.user = user  # ✅ 반드시 연결 필요
        sociallogin.connect(request, user)
        print(f"✅ [SAVE_USER] 저장 완료: {user.email}")
        return user

    def is_open_for_signup(self, request, sociallogin):
        print("⚠️ is_open_for_signup 호출됨")
        return True
