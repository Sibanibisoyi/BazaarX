from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('my-order/', views.my_orders, name='my_orders'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),

]

