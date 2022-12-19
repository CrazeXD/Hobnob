from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import SignupForm, LoginForm

def index(request):
    return render(request, 'index.html')

def call(request):
    return render(request, 'call.html')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Save the user's password separately because the form doesn't include it
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Log the user in and redirect to the home page
            login(request, user)
            return redirect('call')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

def loginuser(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Authenticate the user and log them in
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('call')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})
