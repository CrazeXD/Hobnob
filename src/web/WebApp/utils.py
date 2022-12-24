from .models import *

import random

# Queue Functionality
def add_user_to_queue(user: User) -> QueueItem:
    item: QueueItem = QueueItem.objects.create(user=user)
    item.save()
    return item


def remove_from_queue(user):
    items = QueueItem.objects.all()
    item = items.filter(user=user)
    item.delete()  # NoneType object has no attribute 'delete'
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
    # Code for we have a match
    elif len(matches) <= len(user.recent_calls.all()):
        usertoadd = matches[random.randint(0, len(matches) - 1)]
    else:
        for match in matches:
            if match in user.recent_calls.all():
                matches.remove(match)
        usertoadd = matches[random.randint(0, len(matches) - 1)]
    user.recent_calls.add(usertoadd)
    if len(user.recent_calls.all()) > 5:
        user.recent_calls.remove(user.recent_calls.all()[0])
    remove_from_queue(usertoadd)
    room = ChatRoom.objects.create(user1=user, user2=usertoadd)
    room.save()
    return room