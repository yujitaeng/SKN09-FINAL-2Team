from django.shortcuts import render, redirect
from app.models import User, UserPrefer, PreferType
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.hashers import check_password
from django.conf import settings
import os
from uuid import uuid4

def home(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect('login')

    try:
        profile = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    preferences = UserPrefer.objects.filter(user=profile).select_related('prefer_type')
    prefer_tags = [p.prefer_type.type_name for p in preferences]
    history_data = []  

    return render(request, 'mypage.html', {
        'profile': profile,
        'prefer_tags': prefer_tags,
        'history_data': history_data,
    })


@csrf_protect
def profile_info(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return redirect("login")

    try:
        user = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return redirect("login")

    if request.method == "POST":
        password = request.POST.get("password", "").strip()
        nickname = request.POST.get("nickname", "").strip()
        birth = request.POST.get("birth", "").strip()
        gender = request.POST.get("gender", "").strip()
        job = request.POST.get("job", "").strip()
        delete_image = request.POST.get("delete_image", "")  # "1"이면 삭제
        style_ids = request.POST.getlist("style")
        category_ids = request.POST.getlist("category")

        # if not check_password(password, user.password):
        #     return _render_profile_info_with_error(user, "비밀번호가 올바르지 않습니다.", style_ids, category_ids)

        # 프로필 이미지 업로드 or 삭제 처리
        uploaded_file = request.FILES.get("profile_image")
        if uploaded_file:
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            filename = f"{uuid4().hex}{ext}"
            save_dir = os.path.join(settings.MEDIA_ROOT, "profile_images")
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, filename)
            with open(file_path, "wb+") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            user.profile_image = f"/media/profile_images/{filename}"

        elif delete_image == "1":
            user.profile_image = None

        # 정보 저장
        user.nickname = nickname
        user.birth = birth
        user.gender = gender
        user.job = job
        user.save()

        # 선호 태그 갱신
        UserPrefer.objects.filter(user=user).delete()
        for pid in style_ids + category_ids:
            try:
                pref = PreferType.objects.get(prefer_id=int(pid))
                UserPrefer.objects.create(user=user, prefer_type=pref)
            except PreferType.DoesNotExist:
                continue

        return redirect("mypage")

    # GET 요청 시 사용자 정보, 선호 태그 불러오기
    preferences = UserPrefer.objects.filter(user=user).select_related("prefer_type")
    style_ids = [p.prefer_type.prefer_id for p in preferences if p.prefer_type.type == "스타일"]
    category_ids = [p.prefer_type.prefer_id for p in preferences if p.prefer_type.type == "카테고리"]
    style_options = PreferType.objects.filter(type="스타일")
    category_options = PreferType.objects.filter(type="카테고리")

    return render(request, "profile/profile_info.html", {
        "user": user,
        "style_ids": style_ids,
        "category_ids": category_ids,
        "style_options": style_options,
        "category_options": category_options,
    })


# def _render_profile_info_with_error(user, error_msg, style_ids, category_ids):
#     style_options = PreferType.objects.filter(type="스타일")
#     category_options = PreferType.objects.filter(type="카테고리")
#     return render(None, "profile/profile_info.html", {
#         "user": user,
#         "error": error_msg,
#         "style_ids": [int(sid) for sid in style_ids],
#         "category_ids": [int(cid) for cid in category_ids],
#         "style_options": style_options,
#         "category_options": category_options,
#     })

def profile_password(request):
    return render(request, 'profile/profile_password.html')

def profile_password_confirm(request):
    return render(request, 'profile/profile_password_confirm.html')

def profile_delete(request):
    return render(request, 'profile/profile_delete.html')

def profile_delete_confirm(request):
    return render(request, 'profile/profile_delete_confirm.html')