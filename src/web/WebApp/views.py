from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect

from .forms import SignupForm, LoginForm, SchoolSelector, UserEditForm
from .utils import *


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")


def signup(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form: SignupForm = SignupForm(request.POST)
        if form.is_valid():
            return signup_form_functions(form, request)
    else:
        form: SignupForm = SignupForm()
    return render(request, "signup.html", {"form": form, "error": ""})


def signup_form_functions(form, request):
    user = get_user(form)
    # Get the school from the form
    school = form.cleaned_data["school"]
    if is_generic_name(school) is False:
        return signup_error(
            user, "School not specific enough.", request, form
        )
    # Get user ip
    user_coordinates = form.cleaned_data["location"].split()
    related_schools = find_school_address(school)
    if len(related_schools) == 0:
        user.delete()
        # TODO: #10 Create contact email
        error = '''School not found.
        If you believe this is an error, please contact us at email address.'''
        return signup_error(user, error, request, form)
    distances = get_distances(related_schools, user_coordinates)
    related_schools = check_schools(related_schools, distances)
    if len(related_schools) == 0:
        return signup_error(
            user,
            '''That school is not within range.
            If you believe this is an error, please contact us at email address.''',
            request,
            form,
        )
        # Failed user signup
    if len(related_schools) == 1:
        user.school = list(related_schools.pop().values())[0]
        user.save()
        # Completed user signup
    if len(related_schools) > 1:
        return multiple_schools(related_schools, user, request)
    login(request, user)
    return redirect("call")


def multiple_schools(related_schools, user, request):
    string_template = ''
    for i in related_schools:
        string_template = string_template+i+' '
    user.school = string_template
    user.save()
    login(request, user)
    return redirect(f'schoolvalidation/{string_template}/')


def school_selector(request, schools):
    if request.method == "POST":
        form = SchoolSelector(request.POST)
        if form.is_valid():
            user = request.user
            user.school = form.cleaned_data["school"]
            user.save()
            return redirect("call")
    form = SchoolSelector(schools=schools.split())
    return render(request, "schoolselect.html", {"form": form})


def login_user(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form: LoginForm = LoginForm(request.POST)
        if form.is_valid():
            # Authenticate the user and log them in
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user: User = authenticate(
                request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("call")
    elif request.user.is_authenticated:
        return redirect("call")
    else:
        form: LoginForm = LoginForm()
    return render(request, 'login.html', {"form": form})


def logout_user(request: HttpRequest) -> HttpResponse:
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
def call_homepage(request: HttpRequest) -> HttpResponse:
    return render(request, "callhomepage.html", context={"error": ""})


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
                    chatroom.delete()
                    redirect_url = f"{room_id}/"
                    request.session['users'] = [request.user.username, chatroom.user2.username]
                    return redirect(f"/chatroom/{redirect_url}")
    else:
        room_id: int = pair_func.room_id
        redirect_url = f"/chatroom/{room_id}/"
        request.session['users'] = [pair_func.user1.username, pair_func.user2.username]
        return redirect(redirect_url)


@login_required(login_url="login")
def remove_from_queue_view(request) -> HttpResponse | None:
    if request.method != "POST":
        return None
    remove_from_queue(request.user)
    return HttpResponse("Success")


@login_required(login_url="login")
def video_call(request: HttpRequest, room_id: int) -> HttpResponse:
    if request.user.username not in request.session['users']:
        return redirect("call")

    url = create_room(room_id)
    context = {'url': url, 'username': request.user.username}
    return render(request, 'call.html', context)
