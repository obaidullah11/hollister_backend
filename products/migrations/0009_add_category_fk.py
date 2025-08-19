# Add temporary category_fk field

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_populate_categories'),
    ]

    operations = [
        # Add temporary category_fk field (nullable)
        migrations.AddField(
            model_name='product',
            name='category_fk',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='products_temp',
                to='products.category'
            ),
        ),
    ]

