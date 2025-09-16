from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = 'Populate categories with sample sizes'

    def handle(self, *args, **kwargs):
        categories_data = [
            {
                'name': 'Jeans',
                'description': 'Denim jeans and pants',
                'sizes': [
                    {'value': '28Wx30L', 'display_name': '28W x 30L', 'order': 1, 'is_active': True},
                    {'value': '30Wx30L', 'display_name': '30W x 30L', 'order': 2, 'is_active': True},
                    {'value': '30Wx32L', 'display_name': '30W x 32L', 'order': 3, 'is_active': True},
                    {'value': '32Wx30L', 'display_name': '32W x 30L', 'order': 4, 'is_active': True},
                    {'value': '32Wx32L', 'display_name': '32W x 32L', 'order': 5, 'is_active': True},
                    {'value': '32Wx34L', 'display_name': '32W x 34L', 'order': 6, 'is_active': True},
                    {'value': '34Wx30L', 'display_name': '34W x 30L', 'order': 7, 'is_active': True},
                    {'value': '34Wx32L', 'display_name': '34W x 32L', 'order': 8, 'is_active': True},
                    {'value': '34Wx34L', 'display_name': '34W x 34L', 'order': 9, 'is_active': True},
                    {'value': '36Wx30L', 'display_name': '36W x 30L', 'order': 10, 'is_active': True},
                    {'value': '36Wx32L', 'display_name': '36W x 32L', 'order': 11, 'is_active': True},
                    {'value': '36Wx34L', 'display_name': '36W x 34L', 'order': 12, 'is_active': True},
                ]
            },
            {
                'name': 'Shoes',
                'description': 'Footwear and shoes',
                'sizes': [
                    {'value': '7', 'display_name': '7', 'order': 1, 'is_active': True},
                    {'value': '7.5', 'display_name': '7.5', 'order': 2, 'is_active': True},
                    {'value': '8', 'display_name': '8', 'order': 3, 'is_active': True},
                    {'value': '8.5', 'display_name': '8.5', 'order': 4, 'is_active': True},
                    {'value': '9', 'display_name': '9', 'order': 5, 'is_active': True},
                    {'value': '9.5', 'display_name': '9.5', 'order': 6, 'is_active': True},
                    {'value': '10', 'display_name': '10', 'order': 7, 'is_active': True},
                    {'value': '10.5', 'display_name': '10.5', 'order': 8, 'is_active': True},
                    {'value': '11', 'display_name': '11', 'order': 9, 'is_active': True},
                    {'value': '11.5', 'display_name': '11.5', 'order': 10, 'is_active': True},
                    {'value': '12', 'display_name': '12', 'order': 11, 'is_active': True},
                ]
            },
            {
                'name': 'T-Shirts',
                'description': 'T-shirts and casual tops',
                'sizes': [
                    {'value': 'XS', 'display_name': 'Extra Small', 'order': 1, 'is_active': True},
                    {'value': 'S', 'display_name': 'Small', 'order': 2, 'is_active': True},
                    {'value': 'M', 'display_name': 'Medium', 'order': 3, 'is_active': True},
                    {'value': 'L', 'display_name': 'Large', 'order': 4, 'is_active': True},
                    {'value': 'XL', 'display_name': 'Extra Large', 'order': 5, 'is_active': True},
                    {'value': 'XXL', 'display_name': '2X Large', 'order': 6, 'is_active': True},
                ]
            },
            {
                'name': 'Shirts',
                'description': 'Formal and casual shirts',
                'sizes': [
                    {'value': 'XS', 'display_name': 'Extra Small', 'order': 1, 'is_active': True},
                    {'value': 'S', 'display_name': 'Small', 'order': 2, 'is_active': True},
                    {'value': 'M', 'display_name': 'Medium', 'order': 3, 'is_active': True},
                    {'value': 'L', 'display_name': 'Large', 'order': 4, 'is_active': True},
                    {'value': 'XL', 'display_name': 'Extra Large', 'order': 5, 'is_active': True},
                    {'value': 'XXL', 'display_name': '2X Large', 'order': 6, 'is_active': True},
                ]
            },
            {
                'name': 'Dresses',
                'description': 'Dresses for all occasions',
                'sizes': [
                    {'value': 'XS', 'display_name': 'Extra Small', 'order': 1, 'is_active': True},
                    {'value': 'S', 'display_name': 'Small', 'order': 2, 'is_active': True},
                    {'value': 'M', 'display_name': 'Medium', 'order': 3, 'is_active': True},
                    {'value': 'L', 'display_name': 'Large', 'order': 4, 'is_active': True},
                    {'value': 'XL', 'display_name': 'Extra Large', 'order': 5, 'is_active': True},
                    {'value': 'XXL', 'display_name': '2X Large', 'order': 6, 'is_active': True},
                ]
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'is_active': True,
                    'sizes': cat_data['sizes']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name} with {len(cat_data["sizes"])} sizes'))
            else:
                # Update existing category with sizes if it doesn't have any
                if not category.sizes:
                    category.sizes = cat_data['sizes']
                    category.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'Updated category: {category.name} with {len(cat_data["sizes"])} sizes'))
                else:
                    self.stdout.write(self.style.WARNING(f'Category already exists with sizes: {category.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully processed {created_count} new categories and updated {updated_count} existing categories'))






