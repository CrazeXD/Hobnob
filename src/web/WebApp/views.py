from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from .forms import SignupForm, LoginForm, UserEditForm
from .utils import *


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def signup(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form: SignupForm = SignupForm(request.POST)
        if form.is_valid():
            user: User = form.save()
            # Save the user's password separately because the form doesn't include it
            user.set_password(form.cleaned_data["password"])
            user.save()
            # Log the user in and redirect to the home page
            login(request, user)
            return redirect("call")
    else:
        form: SignupForm = SignupForm()
    return render(request, "signup.html", {"form": form})


def loginuser(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form: LoginForm = LoginForm(request.POST)
        if form.is_valid():
            # Authenticate the user and log them in
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user: User = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("call")
    elif request.user.is_authenticated:
        return redirect("call")
    else:
        form: LoginForm = LoginForm()
    return render(request, 'login.html', {"form": form})


def logoutuser(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("index")


@login_required(login_url="login")
def profile(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form: UserEditForm = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
    else:
        form: UserEditForm = UserEditForm(instance=request.user)
    return render(request, "profile.html", {"form": form})


@login_required(login_url="login")
def callhomepage(request: HttpRequest) -> HttpResponse:
    return render(request, "callhomepage.html")


@login_required(login_url="login")
def add_to_queue(request) -> HttpResponse | None:
    if request.method != "POST":
        return None
    pair_func = pair(request.user)
    if pair_func is None:
        add_user_to_queue(request.user)
        while True:
            chatrooms: QuerySet[ChatRoom] = ChatRoom.objects.all()
            for chatroom in chatrooms:
                if chatroom.user1 == request.user or chatroom.user2 == request.user:
                    room_id = chatroom.room_id
                    partner_user = chatroom.user1 if chatroom.user2 == request.user else chatroom.user2
                    chatroom.delete()
                    return redirect(f"/chatroom/{room_id}/{partner_user.username}")
    else:
        room_id: int = pair_func.room_id
        partner_user = pair_func.user1 if pair_func.user2 == request.user else pair_func.user2
        return redirect(f"/chatroom/{room_id}/{partner_user.username}")

@login_required(login_url="login")
def chat(request: HttpRequest, room_id: int, partner_username: str) -> HttpResponse:
    partner_user: User = User.objects.get(username=partner_username)
    return render(request, "chat.html")
