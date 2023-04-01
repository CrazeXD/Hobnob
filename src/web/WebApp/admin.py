from django.contrib import admin
from .models import User, ChatRoom, QueueItem
# Register your models here.

admin.site.register(User)
admin.site.register(QueueItem)
admin.site.register(ChatRoom)
