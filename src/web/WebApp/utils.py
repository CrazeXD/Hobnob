import time

import requests
from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import geopy.distance
from django.shortcuts import render

from .models import User, QueueItem, ChatRoom

# Signup Functionality


def signup_error(user, error, request, form):
    user.delete()
    return render(request, "signup.html", {"form": form, "error": error})


def get_user(form):
    user: User = form.save()
    # Save the user's password separately because the form doesn't include it
    user.set_password(form.cleaned_data["password"])
    user.save()
    return user


def get_distances(related_schools, user_coordinates):
    school_coordinates = [get_school_coordinates(
        list(i.values())[1]) for i in related_schools]
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
    # Find indexes of distances greater than 50. Remove them from related_schools
    indexpopcount = 0
    for index, i in enumerate(distances):
        if i > 25:
            related_schools.pop(index-indexpopcount)
            indexpopcount += 1
    return related_schools
# Queue Functionality


def add_user_to_queue(user: User):
    # Check if user is already in queue
    items = QueueItem.objects.all()
    if items.filter(user=user):
        return items.filter(user=user)[0]
    # Set user as in queue
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
    if usertoadd == user :
        if len(matches) == 1:
            return None
        matches.remove(user)
        usertoadd = matches[0]
    while usertoadd in user.recent_calls.all(): #While they are in the recent calls
        if any(i not in user.recent_calls.all() for i in matches): #If there is a match that is not in recent calls
            matches.remove(usertoadd)
            usertoadd = matches[0]
        # TODO: Make this in range(2) for production
        elif len(matches) == 1 and any(usertoadd == user.recent_calls.all()[i] for i in range(1)): #If there is only one match and it is in the last 2 calls
            return None
        # If its outside the last 2 calls then it will just use that match
    # Check if someone earlier in the queue can match with the user
    user.recent_calls.add(usertoadd)
    if len(user.recent_calls.all()) > 5:
        user.recent_calls.remove(user.recent_calls.all()[0])
    remove_from_queue(usertoadd)
    room = ChatRoom.objects.create(user1=user, user2=usertoadd)
    room.save()
    return room


def find_school_address(school_name: str):
    """Find the address of a school using the NCES website

    Args:
        school_name (str): Name of school from form

    Returns:
        [{str: str, str:str}]: Name and address of school
    """ 
    url = f"https://nces.ed.gov/ccd/schoolsearch/school_list.asp?Search=1&InstName={school_name.replace(' ','+')}&SchoolID=&Address=&City=&State=&Zip=&Miles=&PhoneAreaCode=&Phone=&DistrictName=&DistrictID=&SchoolType=1&SchoolType=2&SchoolType=3&SchoolType=4&SpecificSchlTypes=all&IncGrade=-1&LoGrade=-1&HiGrade=-1"
    response = requests.get(url)

    # Parse the HTML response
    school_data = response.text
    # Find the line where school_detail.asp is, since it contains the school
    matched_lines = [line for line in school_data.split(
        '\n') if "school_detail.asp" in line]
    schools = []
    # In the line, find the index where the word 'strong' ends
    for matched_line in matched_lines:
        school_starting_index = matched_line.find('strong') + 7
        # Look through the line starting from that index until you find <
        for j in range(school_starting_index, len(matched_line)):
            if matched_line[j] == '<':
                school_ending_index = j
                break
        # The school name is between the two indices
        school_name = matched_line[school_starting_index:school_ending_index]
        address_starting_index = school_ending_index+32
        # Look through the line starting from that index until you find <
        for j in range(address_starting_index, len(matched_line)):
            if matched_line[j] == '<':
                address_ending_index = j
                break
        # The school address is between the two indices
        school_address = matched_line[address_starting_index:address_ending_index]
        school_address = school_address.replace('&nbsp;', ' ')
        # Add the school name and address to the list of schools
        schools.append({'name': school_name, 'address': school_address})
    return schools


def get_school_coordinates(address):
    """Use Geopy to get the coordinates of a school address

    Args:
        address (string): Address of the school

    Returns:
        (int, int): If the address is valid, return the coordinates of the address
        None: If the address is invalid, return None
    """
    address = address.rsplit(' ', 1)[0]
    words_to_nums = {'first': '1st', 'second': '2nd', 'third': '3rd', 'fourth': '4th',
                     'fifth': '5th', 'sixth': '6th', 'seventh': '7th', 'eighth': '8th',
                     'ninth': '9th'}
    for key in list(words_to_nums.keys()):
        if key in address.lower():
            address = address.lower().replace(key, words_to_nums[key])
    geolocator = Nominatim(user_agent="Hobnob")
    try:
        location = geolocator.geocode(address)
    except GeopyError:
        return None
    return None if location is None else (location.latitude, location.longitude)


def get_distance(coordpair1, coordpair2):
    """Gets the distance of the two coordinates in miles

    Args:
        coordpair1 (int, int): Location of user
        coordpair2 (int, int): Location of school

    Returns:
        int: Distance in miles
    """
    return geopy.distance.distance(coordpair1, coordpair2).miles


def is_generic_name(school):
    cases = ['high school', 'middle school', 'elementary school',
             'school', 'elementary', 'middle', 'high']
    if school.lower() in cases:
        return False


def create_room(room_id):
    """Makes an API request to Daily.co to create a room

    Args:
        room_id (int): Room ID

    Returns:
        str: URL of the room
    """
    properties = {"exp": int(time.time())+3600, "max_participants": 2}
    request = requests.post(url='https://api.daily.co/v1/rooms/',
                            headers={
                                "Authorization": "Bearer 63fa0d1c6f80702edb97240b61b2f874d876ceadc450065dc146d49dff0aaa08"},
                            json={"name": str(room_id), "properties": properties}, timeout=5)
    if request.status_code == 200:
        return request.json()['url']
    if request.json()['info'] == f"a room named {room_id} already exists":
        return f"https://hobnob.daily.co/{room_id}" 
