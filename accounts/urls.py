from django.urls import path, include
from . import views

urlpatterns = [
    path('register/', views.register_user, name='registerUser'),

    path('', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    path('user_list/', views.user_list, name='user_list'),

]
