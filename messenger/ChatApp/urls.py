from django.urls import path

from . import views


app_name = 'Chat'
urlpatterns = [
    path('chat_choice/', views.chat_choice, name='chat_choice'),
    path('distribution/', views.distribution, name='distribution'),
    path('save_distribution/', views.save_distribution, name='save_distribution'),
    path('delete_room/<str:room_name>', views.delete_room, name='delete_room'),
    path('<str:room_name>/', views.room, name='room'),
]