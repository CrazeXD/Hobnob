from .models import *

import random

import requests
from geopy.geocoders import Nominatim
import geopy.distance

# Queue Functionality


def add_user_to_queue(user: User) -> QueueItem:
    item: QueueItem = QueueItem.objects.create(user=user)
    item.save()
    return item


def remove_from_queue(user):
    items = QueueItem.objects.all()
    item = items.filter(user=user)
    item.delete()
    return item


def should_pair(user1: User, user2: User) -> bool:
    return user1.school == user2.school


# LOGIC BEFORE I FORGET IT: When new user is added, they call the pair function. The pair function checks if there is
# a valid match. If there is, it creates a new chatroom and returns the room id. If there isn't, it runs an
# asynchronous while true loop that checks if a chatroom with their user is in it. Eventually, another user will run
# the pair function, get a match, and both users will be redirected.
# IT WORKED HAHAHAHHAHAHAHAHHA
def pair(user: User) -> ChatRoom | None:
    items = QueueItem.objects.all()
    matches = [item.user for item in items if should_pair(user, item.user)]
    if not matches:
        return None
    usertoadd = random.choice(matches)
    user.recent_calls.add(usertoadd)
    if len(user.recent_calls.all()) > 5:
        user.recent_calls.remove(user.recent_calls.all()[0])
    remove_from_queue(usertoadd)
    room = ChatRoom.objects.create(user1=user, user2=usertoadd)
    room.save()
    return room


def find_school_address(school_name: str):
    # Convert things like sixth to 6th
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
    address = address.rsplit(' ', 1)[0]
    words_to_nums = {'first': '1st', 'second': '2nd', 'third': '3rd', 'fourth': '4th',
                     'fifth': '5th', 'sixth': '6th', 'seventh': '7th', 'eighth': '8th', 'ninth': '9th'}
    # If any of the keys in words_to_nums are in address (case doesn't matter), replace it with the corresponding value
    for key in words_to_nums:
        if key in address.lower():
            address = address.lower().replace(key, words_to_nums[key])
    geolocator = Nominatim(user_agent="Hobnob")
    try:
        location = geolocator.geocode(address)
    except Exception as e:
        return None

    return None if location is None else (location.latitude, location.longitude)


def get_distance(coordpair1, coordpair2):
    return geopy.distance.distance(coordpair1, coordpair2).miles


def checkSchool(school):
    cases = ['high school', 'middle school', 'elementary school',
             'school', 'elementary', 'middle', 'high']
    if school.lower() in cases:
        return False


def create_room(room_id):
    r = requests.post(url='https://api.daily.co/v1/rooms/', headers={"Authorization": "Bearer 63fa0d1c6f80702edb97240b61b2f874d876ceadc450065dc146d49dff0aaa08"},
                      json={"name": str(room_id)})
    if r.status_code == 200:
        return r.json()['url']
    else:
        return f'https://hobnob.daily.co/{room_id}'

