from django.core.management.base import BaseCommand
from products.models import Category


class Command(BaseCommand):
    help = 'Populate initial categories'

    def handle(self, *args, **kwargs):
        categories = [
            {
                'name': 'Jeans',
                'description': 'Denim jeans and pants'
            },
            {
                'name': 'Shirts',
                'description': 'Formal and casual shirts'
            },
            {
                'name': 'T-Shirts',
                'description': 'T-shirts and casual tops'
            },
            {
                'name': 'Dresses',
                'description': 'Dresses for all occasions'
            },
            {
                'name': 'Pants',
                'description': 'Formal and casual pants'
            },
            {
                'name': 'Shorts',
                'description': 'Shorts and summer wear'
            },
            {
                'name': 'Jackets',
                'description': 'Jackets and outerwear'
            },
            {
                'name': 'Sweaters',
                'description': 'Sweaters and knitwear'
            },
            {
                'name': 'Shoes',
                'description': 'Footwear and shoes'
            }
        ]
        
        created_count = 0
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nTotal categories created: {created_count}'))





