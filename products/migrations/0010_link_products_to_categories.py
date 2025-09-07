# Link products to their categories using the FK field

from django.db import migrations


def link_categories(apps, schema_editor):
    Category = apps.get_model('products', 'Category')
    Product = apps.get_model('products', 'Product')
    
    # Map old category names to new category objects
    category_map = {}
    
    # Build the mapping
    for product in Product.objects.all():
        if product.category and product.category not in category_map:
            # Try to find matching category
            cat_name = product.category.lower().replace(' ', '-')
            try:
                category = Category.objects.get(name=cat_name)
                category_map[product.category] = category
            except Category.DoesNotExist:
                # Try with display_name
                try:
                    category = Category.objects.get(display_name=product.category)
                    category_map[product.category] = category
                except Category.DoesNotExist:
                    print(f"Warning: Category '{product.category}' not found for product {product.name}")
    
    # Update products
    for product in Product.objects.all():
        if product.category in category_map:
            product.category_fk = category_map[product.category]
            product.save()


def unlink_categories(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    # Clear the FK field
    Product.objects.update(category_fk=None)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_add_category_fk'),
    ]

    operations = [
        migrations.RunPython(link_categories, unlink_categories),
    ]





