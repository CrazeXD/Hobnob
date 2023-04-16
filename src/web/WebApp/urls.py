from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('call/', views.call_homepage, name='call'),
    path('signup/', views.signup, name='signup'),
    path('schoolvalidation/<str:schools>/', views.school_selector, name='school'),
    path('login/', views.login_user, name='login'),
    path('profile/', views.profile, name='profile'),
    path('logout/', views.logout_user, name='logout'),
    path('add_to_queue/', views.add_to_queue, name='add_to_queue'),
    path('chatroom/<int:room_id>/', views.video_call, name='chat'),
    path('accept_rules/', views.accept_rules_session, name='accept_rules_session'),
    path('remove_from_queue/', views.remove_user_from_queue, name='remove_from_queue'),
    path('user_in/', views.user_in, name='user_in'),
]
