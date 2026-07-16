from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .forms import ReviewForm
from django.db.models import Avg
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Product, Category, Review, ProductQuestion, ProductVariant
import json




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
    questions = ProductQuestion.objects.filter(product=product).order_by('-created_at')
    user_has_reviewed = False
    in_wishlist = False
    can_review = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(product=product, user=request.user).exists()
        from extras.models import Wishlist
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()
        from orders.models import Order
        can_review = Order.objects.filter(user=request.user, status='delivered', orderitem__product=product).exists()
    review_form = ReviewForm()

    # Build variant data for JS size selector
    variants_qs = product.productvariant_set.all().order_by('value')
    # Keep defined size order
    size_order = ['S', 'M', 'L', 'XL', 'XXL']
    variants_sorted = sorted(variants_qs, key=lambda v: size_order.index(v.value) if v.value in size_order else 99)
    variants_data = [
        {
            'id': v.id,
            'name': v.name,
            'value': v.value,
            'stock': v.stock,
            'price': str(v.effective_price()),
        }
        for v in variants_sorted
    ]
    variant_name = variants_sorted[0].name if variants_sorted else "Option"

    return render(request, 'products/product_detail.html', {
        'product': product,
        'images': image,
        'recently_viewed': recently_viewed_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'review_count': review_count,
        'user_has_reviewed': user_has_reviewed,
        'can_review': can_review,
        'review_form': review_form,
        'in_wishlist': in_wishlist,
        'questions': questions,
        'variants_json': json.dumps(variants_data),
        'variant_name': variant_name,
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
    
    from orders.models import Order
    can_review = Order.objects.filter(user=request.user, status='delivered', orderitem__product=product).exists()
    if not can_review:
        messages.error(request, 'You can only review products that you have purchased and received.')
        return redirect('products:product_detail', slug=slug)

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


def load_more_products(request):
    """AJAX endpoint for infinite scroll on the home page."""
    page_number = request.GET.get('page', 1)
    category_slug = request.GET.get('category', '')

    products = Product.objects.filter(is_active=True)
    if category_slug:
        category = Category.objects.filter(slug=category_slug).first()
        if category:
            products = products.filter(category=category)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(page_number)

    html = render_to_string('products/partials/product_cards.html', {
        'products': page_obj,
    }, request=request)

    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    })


def search_autocomplete(request):
    """AJAX endpoint for live search autocomplete dropdown."""
    query = request.GET.get('q', '').strip()
    results = []

    if len(query) >= 2:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            is_active=True
        ).select_related('category')[:6]

        for p in products:
            results.append({
                'name': p.name,
                'price': str(p.price),
                'category': p.category.name,
                'url': f'/products/{p.slug}/',
                'image': p.image.url if p.image else None,
                'discount': p.discount,
            })

    return JsonResponse({'results': results, 'query': query})


def load_more_category_products(request, slug):
    """AJAX endpoint for infinite scroll on the category page."""
    page_number = request.GET.get('page', 1)
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_active=True)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(page_number)

    html = render_to_string('products/partials/product_cards.html', {
        'products': page_obj,
    }, request=request)

    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    })

@login_required
def ask_question(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        question_text = request.POST.get('question')
        if question_text:
            ProductQuestion.objects.create(
                product = product,
                user = request.user,
                question = question_text,
            )
            messages.success(request, 'Your question has been submitted.')
    return redirect('products:product_detail', slug=slug)



@login_required
def answer_question(request, question_id):
    question = get_object_or_404(ProductQuestion, id=question_id)
    if request.method == 'POST':
        answer_text = request.POST.get('answer')
        if answer_text:
            question.answer = answer_text
            question.is_answered = True
            question.save()
            messages.success(request, 'Answer submitted.')
    return redirect('dashboard:admin_dashboard')




@login_required
def admin_questions(request):
    if not request.user.is_staff:
        return redirect('products:home')
    questions = ProductQuestion.objects.filter(is_answered=False).order_by('-created_at')
    return render(request, 'dashboard/questions.html', {'questions': questions})