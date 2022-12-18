from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def call(request):
    return render(request, 'call.html')
