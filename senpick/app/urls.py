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
from . import views, birth_views, login_views, chat_views

urlpatterns = [
    path('', views.home, name='home'),  # 기본 URL
    # path('about/', views.about, name='about'),  # about 페이지
    path('login/', login_views.home, name='login'),
    path('chat/', chat_views.chat, name='chat'),
    path('login/', login_views.home, name='login'),  # 로그인 페이지
    path('birth/', birth_views.birth, name='birth'),  # 생일 페이지
]
