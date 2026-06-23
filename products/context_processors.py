from products.models import Category
from seller.models import Seller

def categories_processor(request):
    is_seller = False
    if request.user.is_authenticated and not request.user.is_staff:
        is_seller = Seller.objects.filter(user=request.user, is_approved=True).exists()
    return {
        'all_categories': Category.objects.all().order_by('name'),
        'is_seller': is_seller,
    }
