from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignupForm, LoginForm, UserEditForm
from .models import User
def index(request):
    return render(request, "index.html")


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Save the user's password separately because the form doesn't include it
            user.set_password(form.cleaned_data["password"])
            user.save()
            # Log the user in and redirect to the home page
            login(request, user)
            return redirect("call")
    else:
        form = SignupForm()
    return render(request, "signup.html", {"form": form})


def loginuser(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # Authenticate the user and log them in
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("call")
    elif request.user.is_authenticated:
        return redirect("call")
    else:
        form = LoginForm()
    return render(request, 'login.html', {"form": form})


def logoutuser(request):
    logout(request)
    return redirect("index")


def profile(request):
    if not request.user.is_authenticated:
        return redirect("login")
    elif request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form = UserEditForm(instance=request.user)
    return render(request, "profile.html", {"form": form})


def callhomepage(request):
    if not request.user.is_authenticated:
        return redirect("login")
    return render(request, "callhomepage.html")