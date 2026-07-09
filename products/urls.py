from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('compare/', views.compare_products, name='compare_products'),
    path('compare/add/<int:product_id>/',views.add_to_compare,name='add_to_compare'),
    path('category/<slug:slug>/', views.category_page, name='category_page'),
    path('<slug:slug>/review/', views.submit_review, name='submit_review'),
    path('ajax/load-more/', views.load_more_products, name='load_more_products'),
    path('ajax/category/<slug:slug>/load-more/', views.load_more_category_products, name='load_more_category_products'),
    path('ajax/search-autocomplete/', views.search_autocomplete, name='search_autocomplete'),
]

