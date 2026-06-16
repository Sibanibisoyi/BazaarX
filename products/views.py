from django.shortcuts import render, get_object_or_404
from .models import Product, Category
from django.db.models import Q

# Create your views here.
def home(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, 'products/home.html',{
        'products': products,
        'categories':categories,
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    image = product.productimage_set.all()
    return render(request, 'products/product_detail.html', {
    'product': product,
    'images': image,
})

def search(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
    else:
        products = Product.objects.none()
    return render(request, 'products/search.html', {
    'products': products,
    'query': query,
})
