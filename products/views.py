from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Product, Category
from django.db.models import Q
from .models import Review
from .forms import ReviewForm
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


# Create your views here.
def home(request):
    category_slug = request.GET.get('category')
    categories = Category.objects.all()
    selected_category = None
    
    products = Product.objects.filter(is_active=True)
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)
        
    # Get the featured product for the hero banner
    featured_product = Product.objects.filter(is_active=True, is_featured=True).first()

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, 'products/home.html',{
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'featured_product': featured_product,
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

    reviews = Review.objects.filter(product=product).order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    review_count = reviews.count()
    user_has_reviewed = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(product=product, user=request.user).exists()
    review_form = ReviewForm()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'images': image,
        'recently_viewed': recently_viewed_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'user_has_reviewed': user_has_reviewed,
        'review_form': review_form,
    })

def search(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category')
    
    products = Product.objects.filter(is_active=True)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_slug:
        products = products.filter(category__slug=category_slug)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    return render(request, 'products/search.html', {
        'products': page_obj,
        'page_obj': page_obj,
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


def category_page(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/category_page.html', {
        'category': category,
        'products': page_obj,
        'page_obj': page_obj,
    })



@login_required
def submit_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    existing_review = Review.objects.filter(product=product, user=request.user).first()

    if existing_review:
        messages.info(request, 'You have already reviewed this product')
        return redirect('products:product_detail', slug=slug)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Review submitted successfully')
            return redirect('products:product_detail', slug=slug)

    return redirect('products:product_detail', slug=slug)



