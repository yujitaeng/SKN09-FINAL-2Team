from django.shortcuts import render

def birth(request):
    return render(request, 'birth.html')