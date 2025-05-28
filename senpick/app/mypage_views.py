from django.shortcuts import render

def mypage_view(request):
    return render(request, 'mypage.html')