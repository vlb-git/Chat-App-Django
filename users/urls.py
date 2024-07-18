from django.urls import path
from . import views

urlpatterns = [
    path('',views.users_page, name='users_page'),
    path('login/', views.login_page, name='user_login'),
    path('signup/',views.signup_page, name='user_signup'),
    path('signup/entry/',views.signup_entry, name='user_signup_entry'),
    path('login/entry/',views.login_entry, name='user_login_entry'),
    path('logout/',views.logout, name='logout'),
    path('dashboard/',views.dashboard, name='dashboard'),
]
