from django.core.management.base import BaseCommand
from products.models import Category, Product, ProductVariant


class Command(BaseCommand):
    help = 'Create S, M, XL size variants for all products in the Fashion category.'

    def handle(self, *args, **options):
        try:
            fashion = Category.objects.get(name__iexact='fashion')
        except Category.DoesNotExist:
            self.stderr.write(self.style.ERROR('Fashion category not found.'))
            return

        products = Product.objects.filter(category=fashion)
        if not products.exists():
            self.stdout.write(self.style.WARNING('No products found in the Fashion category.'))
            return

        sizes = ['S', 'M', 'XL']
        created_count = 0
        skipped_count = 0

        for product in products:
            for size in sizes:
                obj, created = ProductVariant.objects.get_or_create(
                    product=product,
                    name='Size',
                    value=size,
                    defaults={
                        'stock': 15,
                        'price_override': None,
                    }
                )
                if created:
                    created_count += 1
                    self.stdout.write(f'  Created: {product.name} — Size: {size}')
                else:
                    skipped_count += 1
                    self.stdout.write(self.style.WARNING(
                        f'  Already exists (skipped): {product.name} — Size: {size}'
                    ))

        self.stdout.write(self.style.SUCCESS(
            f'\nDone! {created_count} variant(s) created, {skipped_count} skipped.'
        ))
