from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('approve-seller/<int:seller_id>/', views.approve_seller, name='approve_seller'),
    path('reject-return/<int:return_id>/', views.reject_return, name='reject_return'),
]

