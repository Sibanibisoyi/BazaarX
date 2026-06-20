from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
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
    recently_viewed = request.session.get('recently_viewed', [])
    if product.id not in recently_viewed:
        recently_viewed.insert(0, product.id)
    recently_viewed = recently_viewed[:6]
    request.session['recently_viewed'] = recently_viewed
    recently_viewed_products = Product.objects.filter(
    id__in=recently_viewed).exclude(id=product.id)
    image = product.productimage_set.all()
    return render(request, 'products/product_detail.html', {
    'product': product,
    'images': image,
    'recently_viewed': recently_viewed_products,

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

def add_to_compare(request, product_id):
    compare_list = request.session.get('compare_list', [])

    if product_id not in compare_list:
        if len(compare_list) < 4:
            compare_list.append(product_id)
            messages.success(request, 'Product added to compare')
        else:
            messages.warning(request,'Maximum 4 products can be compared')
    else:
        messages.info(request,'Product already in compare list')

    request.session['compare_list'] = compare_list
    return redirect(request.META.get('HTTP_REFERER', '/'))


def compare_products(request):
    compare_list = request.session.get('compare_list', [])
    products = Product.objects.filter(id__in=compare_list)
    return render(request, 'products/compare.html', {'products': products})