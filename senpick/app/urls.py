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
from . import views
from . import login_views
from . import pswd_views
from . import pswd_verif_views
from . import pswd_gen_views

urlpatterns = [
    path('', views.home, name='home'),  # 기본 URL
    # path('about/', views.about, name='about'),  # about 페이지
    path('login/', login_views.home, name='login'),                  # 로그인
    path('pswd/', pswd_views.home, name='pswd'),                     # 비밀번호 찾기
    path('pswd_verif/', pswd_verif_views.home, name='pswd_verif'),   # 이메일 인증
    path("pswd_gen/", pswd_gen_views.home, name="pswd_gen")          # 비밀번호 생성 
]
