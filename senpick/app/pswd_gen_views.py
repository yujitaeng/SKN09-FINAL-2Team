from django.shortcuts import render

def home(request):
    return render(request, 'pswd_gen.html')