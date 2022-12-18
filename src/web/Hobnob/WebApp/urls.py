from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('call/', views.call, name='call'),
]
