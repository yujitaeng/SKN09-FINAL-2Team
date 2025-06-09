from django.shortcuts import render, redirect

def home(request):
    if not request.session.get('user_id') or request.session.get('type') == 'guest':
        return redirect('login')
    return render(request, 'mypage.html')

def profile_info(request):
    return render(request, 'profile/profile_info.html')

def profile_password(request):
    return render(request, 'profile/profile_password.html')

def profile_password_confirm(request):
    return render(request, 'profile/profile_password_confirm.html')

def profile_delete(request):
    return render(request, 'profile/profile_delete.html')

def profile_delete_confirm(request):
    return render(request, 'profile/profile_delete_confirm.html')