from django.urls import path
from . import views

app_name = 'seller'

urlpatterns = [
    path('register/', views.seller_register, name='seller_register'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('orders/', views.seller_orders, name='seller_orders'),
]

