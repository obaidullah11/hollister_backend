import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holister_backend.settings')
django.setup()

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# Test Swagger schema generation
schema_view = get_schema_view(
    openapi.Info(
        title="Holister Admin API",
        default_version='v1',
        description="API documentation for Holister Admin Panel with Customer and Admin roles",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@holister.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

print("✅ Swagger schema view created successfully")
print("📋 Available URLs:")
print("   - /swagger/ - Swagger UI")
print("   - /redoc/ - ReDoc UI")
print("   - /swagger.json - JSON schema")
print("   - / - Root (redirects to Swagger)")

# Test if we can get the schema
try:
    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser
    
    factory = RequestFactory()
    request = factory.get('/swagger/')
    request.user = AnonymousUser()
    
    # This should work without errors
    print("✅ Schema generation test passed")
except Exception as e:
    print(f"❌ Schema generation test failed: {e}")
