# Generated manually for Terms and Conditions and Privacy Policy models

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TermsAndConditions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Terms and Conditions', max_length=200)),
                ('content', models.TextField()),
                ('version', models.CharField(default='1.0', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Terms and Conditions',
                'verbose_name_plural': 'Terms and Conditions',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PrivacyPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='Privacy Policy', max_length=200)),
                ('content', models.TextField()),
                ('version', models.CharField(default='1.0', max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Privacy Policy',
                'verbose_name_plural': 'Privacy Policies',
                'ordering': ['-created_at'],
            },
        ),
    ]
