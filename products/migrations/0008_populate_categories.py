# Data migration to populate categories from existing product data

from django.db import migrations


def populate_categories(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')
    
    # Get unique categories from existing products
    existing_categories = Product.objects.values_list('category', flat=True).distinct()
    
    # Create category objects
    for cat_name in existing_categories:
        if cat_name:  # Skip empty categories
            # Create category with sensible defaults
            display_name = cat_name
            name = cat_name.lower().replace(' ', '-')
            
            Category.objects.get_or_create(
                name=name,
                defaults={
                    'display_name': display_name,
                    'description': f'{display_name} category',
                    'is_active': True,
                    'order': 0
                }
            )


def reverse_populate(apps, schema_editor):
    # Delete all categories (this will be safe as products still have CharField category)
    Category = apps.get_model('products', 'Category')
    Category.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_add_category_size_models'),
    ]

    operations = [
        migrations.RunPython(populate_categories, reverse_populate),
    ]





