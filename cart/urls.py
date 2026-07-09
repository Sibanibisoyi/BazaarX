from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/', views.update_cart_view, name='update_cart'),
    path('save-for-later/<int:product_id>/', views.save_for_later, name='save_for_later'),
    path('move-to-cart/<int:product_id>/', views.move_to_cart, name='move_to_cart'),
    path('remove-saved/<int:product_id>/', views.remove_saved_item, name='remove_saved_item'),
    path('saved/', views.saved_for_later_list, name='saved_for_later_list'),
]

