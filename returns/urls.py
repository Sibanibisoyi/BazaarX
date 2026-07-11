from django.urls import path
from . import views

app_name = 'returns'

urlpatterns = [
    path('raise/<int:order_id>/', views.raise_return, name='raise_return'),
    path('my-returns/', views.my_returns, name='my_returns'),
    path('approve/<int:return_id>/', views.approve_return, name='approve_return'),
    path('reject/<int:return_id>/', views.reject_return, name='reject_return'),
]

