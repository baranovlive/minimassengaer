from django.urls import path
from .views import \
    RegisterView, LoginView, logout_view, \
    main, settings, user_management, \
    personal_settings, EditNamesView, delete_user, edit_user_img

#Изменения: убрал contacts из импорта


app_name = 'accounts'
urlpatterns = [
    path('', main, name='main'),
    path('settings/', settings, name='settings'),
    path('user_management/', user_management, name='user_management'),
    # path('edit/', edit, name='edit'),
    # path('contacts/', contacts, name='contacts'),
    path('personal_settings/', personal_settings, name='personal_settings'),
    path('edit_user_names/', EditNamesView.as_view(), name='edit_user_names'),
    path('edit_user_img/', edit_user_img, name='edit_user_img'),

    path('delete_user/<int:user_id>', delete_user, name='delete_user'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
]
