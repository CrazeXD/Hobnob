from .models import User, ChatRoom, QueueItem
from django.contrib import admin
# Register your models here.

admin.site.register(User)
admin.site.register(QueueItem)
admin.site.register(ChatRoom)
