from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

import requests
import json
import time

from .forms import SignupForm, LoginForm, SchoolSelector, UserEditForm
from .utils import *


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html")

field_alt_names = {
    "username": "Username",
    "password": "Password",
    "email": "Email",
    "first_name": "First Name",
    "last_name": "Last Name",
    "grade": "Grade",
    "pronouns": "Pronouns",
    "school": "School",
    "user_bio": "Bio",
}
def signup(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form: SignupForm = SignupForm(request.POST)
        if form.is_valid():
            return signup_form_functions(form, request)
        errors = list(form.errors.items())
        for index, error in enumerate(errors):
            if error[0] in field_alt_names:
                error = list(error)
                error[0] = field_alt_names[error[0]]
                errors[index] = tuple(error)

        return render(request, "signup.html", {"form": form, "errors": errors})
    else:
        form: SignupForm = SignupForm()
    return render(request, "signup.html", {"form": form, "errors": None})


def signup_form_functions(form, request):
    user = get_user(form)
    # Get the school from the form
    school = form.cleaned_data["school"].strip()
    if is_generic_name(school) is False:
        return signup_error(
            user, "School not specific enough.", request, form
        )
    user_ip = request.META.get("HTTP_X_REAL_IP")
    ip_response = requests.get(f"https://tools.keycdn.com/geo.json?host={user_ip}", headers={"User-Agent": "keycdn-tools:https://www.hobnob.social"}).json()
    user_coordinates = (ip_response["data"]["geo"]["latitude"], ip_response["data"]["geo"]["longitude"])
    user_state = ip_response["data"]["geo"]["region_code"]
    try:
        user_coordinates = [float(i) for i in user_coordinates]
    except ValueError:
        return signup_error(
            user,
            "Location not found. Please enable location services and try again.",
            request,
            form,
        )
    related_schools = find_school_coordinates(school, user_state)
    if len(related_schools) == 0:
        user.delete()
        error = '''School not found.
        If you believe this is an error, please contact us at meethobnob@gmail.com.'''
        return signup_error(user, error, request, form)
    distances = get_distances(related_schools, user_coordinates)
    related_schools = check_schools(related_schools, distances)
    if len(related_schools) == 0:
        return signup_error(
            user,
            '''That school is not within range.
            If you believe this is an error, please contact us at meethobnob@gmail.com.''',
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
            user = authenticate(
                request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("call")
            else:
                error = "Invalid username or password."
                return render(request, 'login.html', {"form": form, "errors": error})
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
    if 'accepted_rules' not in request.session:
        request.session['accepted_rules'] = "False"
    return render(request, "callhomepage.html", context={"accepted_rules": request.session['accepted_rules']})


@login_required(login_url="login")
def add_to_queue(request) -> JsonResponse | None:
    if request.method != "POST":
        return None
    matched_user_chatroom = pair(request.user)
    if matched_user_chatroom is None:
        solution = parse_rooms(request)
        redirect_url = solution[0]
        request = solution[1]
    else:
        room_id: int = matched_user_chatroom.room_id
        redirect_url = f"/chatroom/{room_id}/"
        request.session['users'] = [str(matched_user_chatroom.user1), str(matched_user_chatroom.user2)]
        timeout = time.time()+15
        while (matched_user_chatroom.user1_in_room is False) and (matched_user_chatroom.user2_in_room is False):
            matched_user_chatroom.refresh_from_db()
            if time.time() > timeout:
                matched_user_chatroom.delete()
                failed_partner = matched_user_chatroom.user1 if matched_user_chatroom.user1 != request.user else matched_user_chatroom.user2
                request.user.recent_calls.remove(failed_partner)
                failed_partner.recent_calls.remove(request.user)
                solution = parse_rooms(request)
                redirect_url = solution[0]
                request = solution[1]
                return JsonResponse({"redirect_url": redirect_url})
    return JsonResponse({"redirect_url": redirect_url})

def remove_user_from_queue(request):
    if request.method != "POST":
        return None
    remove_from_queue(request.user)
    return JsonResponse({"success": True})

@login_required(login_url="login")
def video_call(request: HttpRequest, room_id: int) -> HttpResponse:
    try:
        users = ChatRoom.objects.get(room_id=room_id).user1, ChatRoom.objects.get(room_id=room_id).user2
    except ChatRoom.DoesNotExist:
        return redirect("call")
    if request.user not in users:
        return redirect("call")
    partner = users[1] if users[0] == request.user else users[0]
    partner = User.objects.get(username=partner)
    url = create_room(room_id)
    user_pronouns = "" if request.user.pronouns == "Prefer not to say" else f"({request.user.pronouns})"
    context = {'url': url, 'username': f"{str(request.user)} {user_pronouns}", 'partner_user_name': partner.username, 'partner_user_bio': partner.user_bio, "room_id": room_id}
    return render(request, 'call.html', context)

@login_required(login_url="login")
def accept_rules_session(request: HttpRequest):
    if request.method != "POST":
        return HttpResponse("Error")
    request.session['accepted_rules'] = "True"
    return HttpResponse("Success")

@csrf_exempt
@login_required(login_url="login")
def user_in(request: HttpRequest):
    if request.method != "POST":
        return HttpResponse("Error")
    user = request.user
    room = ChatRoom.objects.get(room_id=json.loads(request.body).get("room_id"))
    if room.user1 == user:
        room.user1_in_room = True
        room.save()
    elif room.user2 == user:
        room.user2_in_room = True
        room.save()
    else:
        return HttpResponse("Error")
    
    return HttpResponse("Success")