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
            return signupFormFunctionality(form, request)
    else:
        form: SignupForm = SignupForm()
    return render(request, "signup.html", {"form": form, "error": ""})


def signupFormFunctionality(form, request):
    user: User = form.save()
    # Save the user's password separately because the form doesn't include it
    user.set_password(form.cleaned_data["password"])
    user.save()
    # Get the school from the form
    school = form.cleaned_data["school"]
    if checkSchool(school) is False:
        user.delete()
        return render(request, "signup.html", {"form": form, "error": "School not specific enough."})
    # Get user ip
    user_coordinates = form.cleaned_data["location"].split()
    related_schools = find_school_address(school)
    if len(related_schools) == 0:
        user.delete()
        # TODO: Create contact email
        return render(request, "signup.html", {"form": form, "error": "School not found. If you believe this is an error, please contact us at email address."})
    # Get the school's coordinates
    school_coordinates = [get_school_coordinates(list(i.values())[1]) for i in related_schools]
    indexes_to_pop = []
    for index, i in enumerate(school_coordinates):
        if i is None:
            indexes_to_pop.append(index)
            school_coordinates.pop(index)
    for indexpopdifference, i in enumerate(indexes_to_pop):
        related_schools.pop(i-indexpopdifference)
    # Get the distance between the user and the school
    distances = [get_distance(tuple(user_coordinates), i) for i in school_coordinates]
    # Find indexes of distances greater than 50. Remove them from related_schools
    indexpopcount = 0
    for index, i in enumerate(distances):
        if i > 50:
            related_schools.pop(index-indexpopcount)
            indexpopcount += 1
    if len(related_schools) == 0:
        # TODO: Create contact email
        user.delete()
        return render(request, "signup.html", {"form": form, "error": "That school is not within range. If you believe this is an error, please contact us at email address."})
        # Failed user signup
    if len(related_schools) == 1:
        user.school = list(related_schools.pop().values())[0]
        user.save()
        # Completed user signup
    if len(related_schools)>1:
        return moreThanOneSchool(related_schools, user, request)
    login(request, user)
    return redirect("call")


def moreThanOneSchool(related_schools, user, request):
    string_template = ''
    for i in related_schools:
        string_template = string_template+i+' '
    user.school = string_template
    user.save()
    login(request, user)
    return redirect(f'schoolvalidation/{string_template}/')

def schoolselector(request, schools):
    if request.method == "POST":
        form = SchoolSelector(request.POST)
        if form.is_valid():
            user = request.user
            user.school = form.cleaned_data["school"]
            user.save()
            return redirect("call")
    form = SchoolSelector(schools=schools.split())
    return render(request, "schoolselect.html", {"form": form})

def loginuser(request: HttpRequest) -> HttpResponse:
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
                    chatroom.delete()
                    return redirect(f"/chatroom/{room_id}/{chatroom.user1.username}/{chatroom.user2.username}")
    else:
        room_id: int = pair_func.room_id
        return redirect(f"/chatroom/{room_id}/{pair_func.user1.username}/{pair_func.user2.username}")


@login_required(login_url="login")
def remove_from_queue_view(request) -> HttpResponse | None:
    if request.method != "POST":
        return None
    remove_from_queue(request.user)
    return HttpResponse("Success")


@login_required(login_url="login")
def video_call(request: HttpRequest, room_id: int, user1: str, user2: str) -> HttpResponse:
    if request.user.username not in [user1, user2]:
        return redirect("call")
    return render(request, 'call.html')
