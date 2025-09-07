# Switch from CharField to ForeignKey

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_link_products_to_categories'),
    ]

    operations = [
        # Remove the old category CharField
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        
        # Rename category_fk to category
        migrations.RenameField(
            model_name='product',
            old_name='category_fk',
            new_name='category',
        ),
        
        # Alter the field to remove null=True (make it required)
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='products',
                to='products.category'
            ),
        ),
    ]





