from django.urls import path
from users.views import register, login_view, logout_view
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.add_address, name='add_address'),
    path('addresses/edit/<int:pk>/', views.edit_address, name='edit_address'),
    path('addresses/delete/<int:pk>/', views.delete_address, name='delete_address'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('points-history/', views.points_history, name='points_history'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('otp-login/', views.otp_login, name='otp_login'),
    path('verify-login-otp/', views.verify_login_otp, name='verify_login_otp'),
    ]