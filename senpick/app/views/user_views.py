from django.shortcuts import render

def home(request):
    return render(request, 'login.html')

def birth(request):
    return render(request, 'birth.html')