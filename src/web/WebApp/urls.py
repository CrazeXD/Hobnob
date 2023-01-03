from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('call/', views.callhomepage, name='call'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.loginuser, name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logoutuser, name='logout'),
    path('add_to_queue/', views.add_to_queue, name='add_to_queue'),
    path('chatroom/<int:room_id>/', views.video_call, name='chat'),
    path('remove_from_queue/', views.remove_from_queue_view, name="remove_from_queue"),
]
