# Generated manually to fix missing color field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_product_category_delete_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='productvariant',
            name='color',
            field=models.CharField(max_length=50, default=''),
            preserve_default=False,
        ),
    ]
