import contextlib
import time

import requests
import geopy.distance
import pandas as pd
from django.shortcuts import render

from .models import User, QueueItem, ChatRoom
from Hobnob import settings
# Signup Functionality

def signup_error(user, error, request, form):
    with contextlib.suppress(ValueError):
        user.delete()
    return render(request, "signup.html", {"form": form, "error": error})


def get_user(form):
    user: User = form.save()
    # Save the user's password separately because the form doesn't include it
    user.set_password(form.cleaned_data["password"])
    user.save()
    return user

def is_generic_name(school):
    cases = ['high school', 'middle school', 'elementary school',
             'school', 'elementary', 'middle', 'high']
    if school.lower() in cases:
        return False


def find_school_coordinates(school_name: str, user_state: str):
    """Find the coordinates of a school using the HIFLD

    Args:
        school_name (str): Name of school from form
        user_state (str): State of user as code

    Returns:
        [{str: str, str:(int, int)}]: Name and coordinates of school
    """
   

    csv = pd.read_csv(settings.BASE_DIR / "assets/schools.csv")
    return [
        {'name': row['NAME'], 'coords': (row['LATITUDE'], row['LONGITUDE'])}
        for index, row in csv.iterrows()
        if school_name.lower() in row['NAME'].lower() and user_state == row['STATE']
    ]


def get_distance(coordpair1, coordpair2):
    """Gets the distance of the two coordinates in miles

    Args:
        coordpair1 (int, int): Location of user
        coordpair2 (int, int): Location of school

    Returns:
        int: Distance in miles
    """
    return geopy.distance.distance(coordpair1, coordpair2).miles


def get_distances(related_schools, user_coordinates):
    school_coordinates = [related_schools[i]["coords"] for i in range(len(related_schools))]
    indexes_to_pop = []
    for index, i in enumerate(school_coordinates):
        if i is None:
            indexes_to_pop.append(index)
            school_coordinates.pop(index)
    for indexpopdifference, i in enumerate(indexes_to_pop):
        related_schools.pop(i-indexpopdifference)
    return [
        get_distance(tuple(user_coordinates), i) for i in school_coordinates
    ]


def check_schools(related_schools, distances):
    indexpopcount = 0
    for index, i in enumerate(distances):
        if i > 25:
            related_schools.pop(index-indexpopcount)
            indexpopcount += 1
    return related_schools

# Queue Functionality


def add_user_to_queue(user: User):
    items = QueueItem.objects.all()
    if items.filter(user=user):
        return items.filter(user=user)[0]
    user.in_queue = True
    user.save()
    item: QueueItem = QueueItem.objects.create(user=user)
    item.save()
    return item


def remove_from_queue(user):
    user.in_queue = False
    user.save()
    items = QueueItem.objects.all()
    item = items.filter(user=user)
    item.delete()
    return item


def should_pair(user1: User, user2: User) -> bool:
    return user1.school == user2.school


def pair(user: User) -> ChatRoom | None:
    items = QueueItem.objects.all()
    matches = [item.user for item in items if should_pair(user, item.user)]
    if not matches:
        return None
    usertoadd = matches[0]
    if usertoadd == user:
        if len(matches) == 1:
            return None
        matches.remove(user)
        usertoadd = matches[0]
    while usertoadd in user.recent_calls.all():
        if any(i not in user.recent_calls.all() for i in matches):
            matches.remove(usertoadd)
            usertoadd = matches[0]
        elif len(matches) == 1 and any(usertoadd == user.recent_calls.all()[i] for i in range(1)):
            return None

    user.recent_calls.add(usertoadd)
    if len(user.recent_calls.all()) > 5:
        user.recent_calls.remove(user.recent_calls.all()[0])
    remove_from_queue(usertoadd)
    room = ChatRoom.objects.create(user1=user, user2=usertoadd)
    room.save()
    return room


def create_room(room_id):
    """Makes an API request to Daily.co to create a room

    Args:
        room_id (int): Room ID

    Returns:
        str: URL of the room
    """
    properties = {"exp": int(time.time())+3600, "max_participants": 2}
    request = requests.post(
        url='https://api.daily.co/v1/rooms/',
        headers={
            "Authorization": f'Bearer {settings.config["DAILY"]["BEARER"]}'
        },
        json={"name": str(room_id), "properties": properties},
        timeout=5,
    )
    if request.status_code == 200:
        return request.json()['url']
    if request.json()['info'] == f"a room named {room_id} already exists":
        return f"https://hobnob.daily.co/{room_id}"
