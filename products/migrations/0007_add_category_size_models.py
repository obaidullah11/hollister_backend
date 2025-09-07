# Generated manually to handle category conversion

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_product_is_active_review'),
    ]

    operations = [
        # Create Category model
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('display_name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0, help_text='Display order (lower numbers appear first)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
                'ordering': ['order', 'name'],
            },
        ),
        
        # Create Size model
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=20)),
                ('display_name', models.CharField(max_length=50)),
                ('order', models.IntegerField(default=0, help_text='Display order within category')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sizes', to='products.category')),
            ],
            options={
                'verbose_name': 'Size',
                'verbose_name_plural': 'Sizes',
                'ordering': ['category', 'order', 'value'],
                'unique_together': {('category', 'value')},
            },
        ),
        
        # Add show_on_homepage field
        migrations.AddField(
            model_name='product',
            name='show_on_homepage',
            field=models.BooleanField(default=False, help_text='Whether to show product on homepage'),
        ),
    ]





