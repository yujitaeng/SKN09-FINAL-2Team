from django.shortcuts import render

def home(request):
    return render(request, 'mypage.html')

def profile_info(request):
    return render(request, 'profile/profile_info.html')

def profile_password(request):
    return render(request, 'profile/profile_password.html')

def profile_delete(request):
    return render(request, 'profile/profile_delete.html')