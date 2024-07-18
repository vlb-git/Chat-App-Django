from django.urls import path
from . import views

urlpatterns = [
    path(r'<str:test_str>/', views.index, name='test_index'),
    path(r'chatwith/<str:username>/', views.chatwith_page, name='chatwith_page'),
    path(r'chatwith/<str:username>/send/', views.chat_with_send, name='chatwith_page_send'),
    path(r'chatwith/<str:username>/get_update/', views.chat_with_update, name='chatwith_page_update'),

    path(r'chatroom/<str:chatroom_name>/', views.chatroom_page, name='chatroom_page'),
    path(r'chatgroup/<str:chatgroup_name>/', views.chatgroup_page, name='chatgroup_page'),
]
    