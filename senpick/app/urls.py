"""
URL configuration for senpick project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import pswd_views
from . import pswd_verif_views
from . import pswd_gen_views
from . import chat_views
from . import views, birth_views, login_views, chat_views, mypage_views
# from app.views import user_views, chat_views, recommend_views

urlpatterns = [
    path('', views.home, name='home'),  # 기본 URL
    # path('about/', views.about, name='about'),  # about 페이지
    path('birth/', birth_views.birth, name='birth'),  # 생일 페이지
    path('login/', login_views.home, name='login'),                  # 로그인
    path('pswd/', pswd_views.home, name='pswd'),                     # 비밀번호 찾기
    path('pswd_verif/', pswd_verif_views.home, name='pswd_verif'),   # 이메일 인증
    path("pswd_gen/", pswd_gen_views.home, name="pswd_gen"),          # 비밀번호 생성 
    path('chat/', chat_views.chat, name='chat'),
    path('mypage/', mypage_views.home, name='mypage'),
    path('mypage/profile/', mypage_views.profile_info, name='profile_info'),
    path('mypage/profile/password/', mypage_views.profile_password, name='profile_password'),
    path('mypage/profile/password/confirm', mypage_views.profile_password_confirm, name='profile_password_confirm'),
    path('mypage/profile/delete/', mypage_views.profile_delete, name='profile_delete'),
    path('mypage/profile/delete/confirm', mypage_views.profile_delete_confirm, name='profile_delete_confirm'),
    path('signup/step1/', views.signup_step1, name='signup_step1'),
    path('signup/step2/', views.signup_step2, name='signup_step2'),
    path('signup/step4/', views.signup_step4, name='signup_step4'),
    path('signup/step5/', views.signup_step5, name='signup_step5'),
    path('signup/send-code/', views.send_verification_code, name='send_verification_code'),
    path('signup/verify-code/', views.verify_code, name='verify_code'),
]
