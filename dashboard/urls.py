from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('approve-seller/<int:seller_id>/', views.approve_seller, name='approve_seller'),
    path('reject-return/<int:return_id>/', views.reject_return, name='reject_return'),
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('products/', views.admin_products, name='admin_products'),
    path('products/add/', views.admin_add_product, name='admin_add_product'),
    path('products/<int:product_id>/edit/', views.admin_edit_product, name='admin_edit_product'),
    path('products/<int:product_id>/delete/', views.admin_delete_product, name='admin_delete_product'),
    path('orders/', views.admin_orders, name='admin_orders'),
    path('orders/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('orders/<int:order_id>/update-status/', views.admin_update_status, name='admin_update_status'),
    path('categories/', views.admin_categories, name='admin_categories'),
    path('categories/add/', views.admin_add_category, name='admin_add_category'),
    path('categories/<int:category_id>/edit/', views.admin_edit_category, name='admin_edit_category'),
    path('categories/<int:category_id>/delete/', views.admin_delete_category, name='admin_delete_category'),
]

