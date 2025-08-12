import os
import django
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'holister_backend.settings')
django.setup()

print("🔍 Debugging Swagger Configuration...")

# Test 1: Check if drf-yasg is properly installed
try:
    import drf_yasg
    print("✅ drf-yasg is installed")
except ImportError as e:
    print(f"❌ drf-yasg import failed: {e}")
    sys.exit(1)

# Test 2: Check if it's in INSTALLED_APPS
from django.conf import settings
if 'drf_yasg' in settings.INSTALLED_APPS:
    print("✅ drf_yasg is in INSTALLED_APPS")
else:
    print("❌ drf_yasg is NOT in INSTALLED_APPS")

# Test 3: Check URL patterns
from django.urls import get_resolver
resolver = get_resolver()
print(f"✅ URL resolver loaded with {len(resolver.url_patterns)} patterns")

# Test 4: Check if swagger URLs are accessible
try:
    from django.test import RequestFactory
    from django.contrib.auth.models import AnonymousUser
    
    factory = RequestFactory()
    
    # Test swagger endpoint
    request = factory.get('/swagger/')
    request.user = AnonymousUser()
    print("✅ Request factory created")
    
    # Test the actual view
    from holister_backend.urls import schema_view
    response = schema_view.with_ui('swagger', cache_timeout=0)(request)
    print(f"✅ Swagger view response status: {response.status_code}")
    
except Exception as e:
    print(f"❌ Swagger view test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check for any view decorators that might cause issues
print("\n🔍 Checking for potential issues...")

# Check if any views have problematic decorators
try:
    from accounts.views import *
    from products.views import *
    from orders.views import *
    print("✅ All view imports successful")
except Exception as e:
    print(f"❌ View import issue: {e}")

print("\n📋 Swagger should be available at:")
print("   - http://127.0.0.1:8000/swagger/")
print("   - http://127.0.0.1:8000/redoc/")
print("   - http://127.0.0.1:8000/ (root)")
