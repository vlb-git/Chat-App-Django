from django.urls import path
from . import views

urlpatterns = [
    path('', views.members, name='members'),
    path('test/',views.members_test, name='members_test'),
]