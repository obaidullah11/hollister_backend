# Revert category from ForeignKey to CharField

from django.db import migrations, models


def convert_category_to_string(apps, schema_editor):
    """Convert category ForeignKey references back to string values"""
    Product = apps.get_model('products', 'Product')
    
    for product in Product.objects.all():
        if product.category:
            # Get the category display name
            product.category_string = product.category.display_name
            product.save()


def reverse_convert(apps, schema_editor):
    """This would convert strings back to ForeignKeys but we won't implement it"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_switch_category_fields'),
    ]

    operations = [
        # First add a temporary field to store the string value
        migrations.AddField(
            model_name='product',
            name='category_string',
            field=models.CharField(max_length=100, default=''),
        ),
        
        # Convert the data
        migrations.RunPython(convert_category_to_string, reverse_convert),
        
        # Remove the ForeignKey field
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        
        # Rename category_string to category
        migrations.RenameField(
            model_name='product',
            old_name='category_string',
            new_name='category',
        ),
    ]





