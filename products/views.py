from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q, Count
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Product, ProductVariant, ProductSize, Review, Category
from .serializers import (
    ProductSerializer, ProductCreateSerializer, ProductUpdateSerializer,
    ProductVariantSerializer, ProductVariantCreateSerializer, ProductVariantUpdateSerializer,
    EnhancedProductCreateSerializer, ProductImageSerializer, ProductDetailSerializer,
    ReviewSerializer, ReviewCreateSerializer, CategorySerializer
)

# Product Views
class ProductListView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'gender', 'is_active']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'selling_price', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()
        
        queryset = Product.objects.prefetch_related(
            'variants', 'variants__sizes'
        )
        
        # Filter by is_active for non-admin users
        if not self.request.user.is_admin:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductSerializer

class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response({
                'success': True,
                'message': 'Product created successfully',
                'data': ProductSerializer(product).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Product creation failed',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class EnhancedProductCreateView(generics.CreateAPIView):
    """
    Enhanced product creation view that handles multiple variants with images in one call.
    Expects multipart/form-data with array-style field names for variants.
    """
    serializer_class = EnhancedProductCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        print("\n" + "="*80)
        print("🚀 ENHANCED PRODUCT CREATE VIEW - START")
        print("="*80)
        
        # Debug: Print the incoming request details
        print(f"🔍 Request Method: {request.method}")
        print(f"🔍 Content-Type: {request.content_type}")
        print(f"🔍 Content-Length: {request.headers.get('Content-Length', 'Unknown')}")
        print(f"🔍 User: {request.user}")
        print()
        
        # Debug: Print all request data
        print("📊 REQUEST.DATA CONTENTS:")
        print("-" * 40)
        for key, value in request.data.items():
            print(f"  {key}: {type(value)} = {repr(value)}")
        print()
        
        # Debug: Print all files
        print("📁 REQUEST.FILES CONTENTS:")
        print("-" * 40)
        for key, value in request.FILES.items():
            print(f"  {key}: {type(value)} = {value.name if hasattr(value, 'name') else value}")
        print()
        
        # Debug: Print all headers
        print("📋 REQUEST HEADERS:")
        print("-" * 40)
        for key, value in request.headers.items():
            if key.lower() in ['authorization', 'content-type', 'content-length']:
                print(f"  {key}: {value}")
        print()
        
        # Parse multipart form data to extract variants
        print("🔧 PARSING VARIANTS...")
        variants_data = self._parse_variants_from_form_data(request.data, request.FILES)
        
        print(f"✅ PARSED VARIANTS RESULT:")
        print(f"  Type: {type(variants_data)}")
        print(f"  Length: {len(variants_data) if isinstance(variants_data, list) else 'N/A'}")
        print(f"  Content: {variants_data}")
        print()
        
        # Create a copy of data and add parsed variants
        data = request.data.copy()
        data['variants'] = variants_data
        
        # Map frontend fields to model fields
        print("🔧 MAPPING FIELDS...")
        mapped_data = {}
        
        # Direct mappings
        field_mappings = {
            'name': 'name',
            'sku': 'sku',
            'description': 'description',
            'category': 'category',
            'gender': 'gender',
            'selling_price': 'selling_price',
            'purchasing_price': 'purchasing_price',
            'material_and_care': 'material_and_care'
        }
        
        for frontend_field, model_field in field_mappings.items():
            if frontend_field in data:
                mapped_data[model_field] = data[frontend_field]
                print(f"  {frontend_field} → {model_field}: {data[frontend_field]}")
            else:
                print(f"  ❌ Missing field: {frontend_field}")
        
        # Handle special cases
        if 'cost_price' in data:
            mapped_data['purchasing_price'] = data['cost_price']
            print(f"  cost_price → purchasing_price: {data['cost_price']}")
        
        if 'brand' in data:
            # Map brand to gender if needed
            brand = data['brand'].lower()
            if brand in ['men', 'male']:
                mapped_data['gender'] = 'men'
            elif brand in ['women', 'female']:
                mapped_data['gender'] = 'women'
            elif brand in ['unisex']:
                mapped_data['gender'] = 'unisex'
            elif brand in ['kids', 'children']:
                mapped_data['gender'] = 'kids'
            print(f"  brand → gender: {data['brand']} → {mapped_data.get('gender')}")
        
        # Add variants
        mapped_data['variants'] = variants_data
        
        print("📝 FINAL MAPPED DATA FOR SERIALIZER:")
        print("-" * 40)
        for key, value in mapped_data.items():
            print(f"  {key}: {type(value)} = {repr(value)}")
        print()
        
        # Validate serializer
        print("🔍 VALIDATING SERIALIZER...")
        serializer = self.get_serializer(data=mapped_data)
        
        if serializer.is_valid():
            print("✅ SERIALIZER VALIDATION PASSED!")
            print("💾 SAVING PRODUCT...")
            product = serializer.save()
            print(f"✅ PRODUCT SAVED! ID: {product.id}")
            
            # Get the response data
            response_data = ProductSerializer(product).data
            print("📤 RESPONSE DATA:")
            print(f"  Product ID: {response_data.get('id')}")
            print(f"  Product Name: {response_data.get('name')}")
            print(f"  Variants Count: {len(response_data.get('variants', []))}")
            
            print("="*80)
            print("🚀 ENHANCED PRODUCT CREATE VIEW - SUCCESS")
            print("="*80)
            
            return Response({
                'success': True,
                'message': 'Product with variants created successfully',
                'data': response_data
            }, status=status.HTTP_201_CREATED)
        
        print("❌ SERIALIZER VALIDATION FAILED!")
        print("🔍 VALIDATION ERRORS:")
        print("-" * 40)
        for field, errors in serializer.errors.items():
            print(f"  {field}: {errors}")
        print()
        
        print("="*80)
        print("🚀 ENHANCED PRODUCT CREATE VIEW - FAILED")
        print("="*80)
        
        return Response({
            'success': False,
            'message': 'Product creation failed',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _parse_variants_from_form_data(self, data, files):
        """
        Parse multipart form data to extract variants array.
        Handles different data structures from frontend.
        """
        print("🔧 _parse_variants_from_form_data called")
        print(f"  Input data type: {type(data)}")
        print(f"  Input files type: {type(files)}")
        print(f"  Data keys: {list(data.keys())}")
        print(f"  Files keys: {list(files.keys())}")
        
        variants = []
        
        # Method 1: Check if variants is already a list (Frontend sends this way)
        print("🔧 Method 1: Checking if variants is already a list...")
        if 'variants' in data and isinstance(data['variants'], list):
            print(f"✅ Method 1 succeeded: variants is already a list with {len(data['variants'])} items")
            # Process the variants to match expected format
            processed_variants = []
            for i, variant in enumerate(data['variants']):
                print(f"  Processing variant {i}: {variant}")
                
                processed_variant = {}
                
                # Handle name
                if 'name' in variant:
                    processed_variant['name'] = str(variant['name'])
                    print(f"    Name: {processed_variant['name']}")
                else:
                    print(f"    ❌ Missing name for variant {i}")
                    continue
                
                # Handle color
                if 'color' in variant:
                    processed_variant['color'] = str(variant['color'])
                    print(f"    Color: {processed_variant['color']}")
                else:
                    print(f"    ❌ Missing color for variant {i}")
                    continue
                
                # Handle stock (convert from stock_quantity if needed)
                if 'stock' in variant:
                    stock_value = variant['stock']
                elif 'stock_quantity' in variant:
                    stock_value = variant['stock_quantity']
                else:
                    stock_value = 0
                
                try:
                    processed_variant['stock'] = int(stock_value)
                    print(f"    Stock: {processed_variant['stock']}")
                except (ValueError, TypeError) as e:
                    print(f"    Stock conversion failed: {e}")
                    processed_variant['stock'] = 0
                
                # Handle sizes (convert from array to string if needed)
                if 'sizes' in variant:
                    sizes_data = variant['sizes']
                    if isinstance(sizes_data, list):
                        processed_variant['sizes'] = [str(size) for size in sizes_data]
                        print(f"    Sizes (from array): {processed_variant['sizes']}")
                    elif isinstance(sizes_data, str):
                        processed_variant['sizes'] = [size.strip() for size in sizes_data.split(',')]
                        print(f"    Sizes (from string): {processed_variant['sizes']}")
                    else:
                        processed_variant['sizes'] = []
                        print(f"    Sizes (unknown type): {sizes_data}")
                else:
                    processed_variant['sizes'] = []
                    print(f"    Sizes: Not found")
                
                # Handle image files if present
                if 'variant_icon' in variant:
                    processed_variant['variant_icon'] = variant['variant_icon']
                    print(f"    Icon: {variant['variant_icon']}")
                
                if 'variant_picture' in variant:
                    processed_variant['variant_picture'] = variant['variant_picture']
                    print(f"    Picture: {variant['variant_picture']}")
                
                # Only add variant if it has required fields
                if processed_variant['name'] and processed_variant['color']:
                    processed_variants.append(processed_variant)
                    print(f"    ✅ Variant {i} processed and added")
                else:
                    print(f"    ❌ Variant {i} skipped - missing required fields")
            
            print(f"  Total processed variants: {len(processed_variants)}")
            return processed_variants
        
        # Method 2: Try to parse array-style field names
        print("🔧 Method 2: Trying array-style field names...")
        variants_data = self._parse_array_style_fields(data, files)
        if variants_data:
            print(f"✅ Method 2 succeeded: {len(variants_data)} variants found")
            return variants_data
        print("❌ Method 2 failed")
        
        # Method 3: Try to parse if variants is a JSON string
        print("🔧 Method 3: Checking if variants is a JSON string...")
        if 'variants' in data and isinstance(data['variants'], str):
            try:
                import json
                parsed_variants = json.loads(data['variants'])
                if isinstance(parsed_variants, list):
                    print(f"✅ Method 3 succeeded: parsed JSON variants with {len(parsed_variants)} items")
                    return parsed_variants
            except (json.JSONDecodeError, TypeError) as e:
                print(f"❌ Method 3 failed: JSON decode error - {e}")
        print("❌ Method 3 failed")
        
        # Method 4: Try to parse individual variant fields
        print("🔧 Method 4: Checking for individual variant fields...")
        variants_data = self._parse_individual_variant_fields(data, files)
        if variants_data:
            print(f"✅ Method 4 succeeded: {len(variants_data)} variants found")
            return variants_data
        print("❌ Method 4 failed")
        
        # Method 5: Try to parse variant_0_name style fields
        print("🔧 Method 5: Checking for variant_0_name style fields...")
        variants_data = self._parse_variant_indexed_fields(data, files)
        if variants_data:
            print(f"✅ Method 5 succeeded: {len(variants_data)} variants found")
            return variants_data
        print("❌ Method 5 failed")
        
        print("❌ All parsing methods failed - returning empty list")
        return []
    
    def _parse_array_style_fields(self, data, files):
        """Parse variants[0][name] style fields"""
        print("🔧 _parse_array_style_fields called")
        variants = []
        variant_index = 0
        
        while True:
            # Check if we have a variant at this index
            name_key = f'variants[{variant_index}][name]'
            if name_key not in data:
                print(f"  No more variants found at index {variant_index}")
                break
            
            print(f"  Found variant at index {variant_index}")
            variant_data = {}
            
            # Extract basic fields
            variant_data['name'] = data.get(f'variants[{variant_index}][name]', '')
            variant_data['color'] = data.get(f'variants[{variant_index}][color]', '')
            stock_value = data.get(f'variants[{variant_index}][stock]', 0)
            
            print(f"    Name: {variant_data['name']}")
            print(f"    Color: {variant_data['color']}")
            print(f"    Stock (raw): {stock_value} (type: {type(stock_value)})")
            
            # Convert stock to integer
            try:
                variant_data['stock'] = int(stock_value)
                print(f"    Stock (converted): {variant_data['stock']}")
            except (ValueError, TypeError) as e:
                print(f"    Stock conversion failed: {e}")
                variant_data['stock'] = 0
            
            # Extract image files
            icon_key = f'variants[{variant_index}][variant_icon]'
            if icon_key in files and files[icon_key]:
                variant_data['variant_icon'] = files[icon_key]
                print(f"    Icon: {files[icon_key].name}")
            else:
                print(f"    Icon: Not found or empty")
            
            picture_key = f'variants[{variant_index}][variant_picture]'
            if picture_key in files and files[picture_key]:
                variant_data['variant_picture'] = files[picture_key]
                print(f"    Picture: {files[picture_key].name}")
            else:
                print(f"    Picture: Not found or empty")
            
            # Extract sizes
            sizes_key = f'variants[{variant_index}][sizes]'
            if sizes_key in data:
                sizes_str = data[sizes_key]
                print(f"    Sizes (raw): {sizes_str} (type: {type(sizes_str)})")
                if isinstance(sizes_str, str):
                    variant_data['sizes'] = [size.strip() for size in sizes_str.split(',')]
                    print(f"    Sizes (parsed): {variant_data['sizes']}")
                else:
                    variant_data['sizes'] = sizes_str
                    print(f"    Sizes (direct): {variant_data['sizes']}")
            else:
                print(f"    Sizes: Not found")
            
            # Only add variant if it has required fields
            if variant_data['name'] and variant_data['color']:
                variants.append(variant_data)
                print(f"    ✅ Variant added to list")
            else:
                print(f"    ❌ Variant skipped - missing name or color")
            
            variant_index += 1
        
        print(f"  Total variants parsed: {len(variants)}")
        return variants
    
    def _parse_individual_variant_fields(self, data, files):
        """Parse individual variant fields if they exist"""
        variants = []
        
        # Look for variant fields in the data
        variant_fields = {}
        for key, value in data.items():
            if key.startswith('variant_'):
                variant_fields[key] = value
        
        if variant_fields:
            # This might be a single variant
            variant_data = {}
            variant_data['name'] = data.get('variant_name', '')
            variant_data['color'] = data.get('variant_color', '')
            variant_data['stock'] = int(data.get('variant_stock', 0))
            
            # Handle sizes
            sizes_str = data.get('variant_sizes', '')
            if sizes_str:
                variant_data['sizes'] = [size.strip() for size in sizes_str.split(',')]
            
            if variant_data['name'] and variant_data['color']:
                variants.append(variant_data)
        
        return variants
    
    def _parse_variant_indexed_fields(self, data, files):
        """Parse variant_0_name, variant_0_color style fields"""
        print("🔧 _parse_variant_indexed_fields called")
        variants = []
        variant_index = 0
        
        while True:
            # Check if we have a variant at this index
            name_key = f'variant_{variant_index}_name'
            if name_key not in data:
                print(f"  No more variants found at index {variant_index}")
                break
            
            print(f"  Found variant at index {variant_index}")
            variant_data = {}
            
            # Extract basic fields
            variant_data['name'] = data.get(f'variant_{variant_index}_name', '')
            variant_data['color'] = data.get(f'variant_{variant_index}_color', '')
            # Handle both stock and stock_quantity field names
            stock_value = data.get(f'variant_{variant_index}_stock_quantity', 
                                 data.get(f'variant_{variant_index}_stock', 0))
            
            print(f"    Name: {variant_data['name']}")
            print(f"    Color: {variant_data['color']}")
            print(f"    Stock (raw): {stock_value} (type: {type(stock_value)})")
            
            # Convert stock to integer
            try:
                variant_data['stock'] = int(stock_value)
                print(f"    Stock (converted): {variant_data['stock']}")
            except (ValueError, TypeError) as e:
                print(f"    Stock conversion failed: {e}")
                variant_data['stock'] = 0
            
            # Extract image files
            icon_key = f'variant_{variant_index}_icon'
            if icon_key in files and files[icon_key]:
                variant_data['variant_icon'] = files[icon_key]
                print(f"    Icon: {files[icon_key].name}")
            else:
                print(f"    Icon: Not found or empty")
            
            picture_key = f'variant_{variant_index}_image'
            if picture_key in files and files[picture_key]:
                variant_data['variant_picture'] = files[picture_key]
                print(f"    Picture: {files[picture_key].name}")
            else:
                print(f"    Picture: Not found or empty")
            
            # Extract sizes
            sizes_key = f'variant_{variant_index}_sizes'
            if sizes_key in data:
                sizes_str = data[sizes_key]
                print(f"    Sizes (raw): {sizes_str} (type: {type(sizes_str)})")
                if isinstance(sizes_str, str):
                    variant_data['sizes'] = [size.strip() for size in sizes_str.split(',')]
                    print(f"    Sizes (parsed): {variant_data['sizes']}")
                else:
                    variant_data['sizes'] = sizes_str
                    print(f"    Sizes (direct): {variant_data['sizes']}")
            else:
                print(f"    Sizes: Not found")
            
            # Only add variant if it has required fields
            if variant_data['name'] and variant_data['color']:
                variants.append(variant_data)
                print(f"    ✅ Variant added to list")
            else:
                print(f"    ❌ Variant skipped - missing name or color")
            
            variant_index += 1
        
        print(f"  Total variants parsed: {len(variants)}")
        return variants

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.prefetch_related(
        'variants', 'variants__sizes'
    )
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductUpdateSerializer
        return ProductDetailSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to return consistent response format"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        # Debug logging
        print(f"🔍 ProductDetailView.retrieve - Product ID: {instance.id}")
        print(f"🔍 ProductDetailView.retrieve - Product Name: {instance.name}")
        print(f"🔍 ProductDetailView.retrieve - Variants count: {instance.variants.count()}")
        
        serialized_data = serializer.data
        print(f"🔍 ProductDetailView.retrieve - Serialized variants: {serialized_data.get('variants', [])}")
        
        return Response({
            'success': True,
            'message': 'Product details retrieved successfully',
            'data': serialized_data
        })
    
    def destroy(self, request, *args, **kwargs):
        product = self.get_object()
        product.delete()
        return Response({
            'success': True,
            'message': 'Product deleted successfully'
        }, status=status.HTTP_200_OK)

# Product Variant Views
class ProductVariantListView(generics.ListCreateAPIView):
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ProductVariant.objects.none()
        product_id = self.kwargs.get('product_id')
        return ProductVariant.objects.filter(product_id=product_id).prefetch_related('sizes')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductVariantCreateSerializer
        return ProductVariantSerializer

class ProductVariantCreateView(generics.CreateAPIView):
    serializer_class = ProductVariantCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            variant = serializer.save(product=product)
            return Response({
                'success': True,
                'message': 'Product variant created successfully',
                'data': ProductVariantSerializer(variant).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': 'Product variant creation failed',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ProductVariantDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductVariant.objects.prefetch_related('sizes')
    serializer_class = ProductVariantSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ProductVariantUpdateSerializer
        return ProductVariantSerializer

# Product Image Views
class ProductImageCreateView(generics.CreateAPIView):
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Handle image upload logic here
        # For now, return a placeholder response
        return Response({
            'success': True,
            'message': 'Image upload endpoint - implementation needed',
            'data': {'product_id': product_id}
        }, status=status.HTTP_201_CREATED)

# Admin Views
class AdminProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'gender']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'selling_price', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()
        return Product.objects.prefetch_related(
            'variants', 'variants__sizes'
        )
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'message': 'Admin product list retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def product_stats(request):
    """
    Get product statistics for admin dashboard
    """
    total_products = Product.objects.count()
    total_variants = ProductVariant.objects.count()
    total_stock = sum(variant.stock for variant in ProductVariant.objects.all())
    
    return Response({
        'success': True,
        'message': 'Product statistics retrieved successfully',
        'data': {
            'total_products': total_products,
            'total_variants': total_variants,
            'total_stock': total_stock
        }
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def category_stats(request):
    """
    Get category statistics for admin dashboard
    """
    categories = Product.objects.values('category').annotate(
        product_count=Count('id')
    )
    
    return Response({
        'success': True,
        'message': 'Category statistics retrieved successfully',
        'data': list(categories)
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def bulk_update_stock(request):
    """
    Bulk update stock for multiple variants
    """
    variants_data = request.data.get('variants', [])
    updated_variants = []
    
    for variant_data in variants_data:
        variant_id = variant_data.get('id')
        new_stock = variant_data.get('stock')
        
        try:
            variant = ProductVariant.objects.get(id=variant_id)
            variant.stock = new_stock
            variant.save()
            updated_variants.append({
                'id': variant.id,
                'name': variant.name,
                'stock': variant.stock
            })
        except ProductVariant.DoesNotExist:
            continue
    
    return Response({
        'success': True,
        'message': f'Updated stock for {len(updated_variants)} variants',
        'data': updated_variants
    }, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_product_view(request, pk):
    """
    Permanently delete product
    """
    if not request.user.is_admin:
        return Response({
            'success': False,
            'message': 'Admin access required'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Store product info before deletion for response
    product_info = {
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'category': product.category
    }
    
    # Permanently delete the product
    product.delete()
    
    return Response({
        'success': True,
        'message': 'Product permanently deleted',
        'data': {
            'deleted_product': product_info
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def debug_request_data(request):
    """Debug endpoint to see what data structure is being sent"""
    print("\n" + "="*80)
    print("🔍 DEBUG ENDPOINT - START")
    print("="*80)
    
    print(f"🔍 Request Method: {request.method}")
    print(f"🔍 Content-Type: {request.content_type}")
    print(f"🔍 Content-Length: {request.headers.get('Content-Length', 'Unknown')}")
    print(f"🔍 User: {request.user}")
    print()
    
    print("📊 REQUEST.DATA CONTENTS:")
    print("-" * 40)
    for key, value in request.data.items():
        print(f"  {key}: {type(value)} = {repr(value)}")
    print()
    
    print("📁 REQUEST.FILES CONTENTS:")
    print("-" * 40)
    for key, value in request.FILES.items():
        print(f"  {key}: {type(value)} = {value.name if hasattr(value, 'name') else value}")
    print()
    
    print("📋 REQUEST HEADERS:")
    print("-" * 40)
    for key, value in request.headers.items():
        if key.lower() in ['authorization', 'content-type', 'content-length']:
            print(f"  {key}: {value}")
    print()
    
    print("🔍 DATA ANALYSIS:")
    print("-" * 40)
    
    # Check for variants data
    variants_keys = [key for key in request.data.keys() if 'variant' in key.lower()]
    if variants_keys:
        print(f"  Found {len(variants_keys)} variant-related keys:")
        for key in variants_keys:
            print(f"    {key}: {type(request.data[key])} = {repr(request.data[key])}")
    else:
        print("  No variant-related keys found")
    
    # Check for array-style keys
    array_keys = [key for key in request.data.keys() if '[' in key and ']' in key]
    if array_keys:
        print(f"  Found {len(array_keys)} array-style keys:")
        for key in array_keys:
            print(f"    {key}: {type(request.data[key])} = {repr(request.data[key])}")
    else:
        print("  No array-style keys found")
    
    print()
    
    print("="*80)
    print("🔍 DEBUG ENDPOINT - END")
    print("="*80)
    
    return Response({
        'success': True,
        'message': 'Request data logged to console',
        'data': {
            'content_type': request.content_type,
            'data_keys': list(request.data.keys()),
            'files_keys': list(request.FILES.keys()),
            'data_sample': {k: str(v)[:100] for k, v in request.data.items()},
            'files_sample': {k: str(v)[:100] for k, v in request.FILES.items()},
            'variant_keys': [key for key in request.data.keys() if 'variant' in key.lower()],
            'array_keys': [key for key in request.data.keys() if '[' in key and ']' in key]
        }
    })


# Review Views
class ReviewListCreateView(generics.ListCreateAPIView):
    """
    List all reviews for a product or create a new review.
    Only authenticated users can create reviews.
    One review per user per product.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating', 'helpful_votes']
    ordering = ['-created_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Review.objects.none()
        
        product_id = self.kwargs.get('product_id')
        return Review.objects.filter(product_id=product_id).select_related('user')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    @swagger_auto_schema(
        operation_description="List all reviews for a product",
        responses={
            200: openapi.Response(
                description="Reviews retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT))
                    }
                )
            )
        }
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'message': 'Reviews retrieved successfully',
            'data': serializer.data
        })
    
    @swagger_auto_schema(
        operation_description="Create a new review for a product",
        request_body=ReviewCreateSerializer,
        responses={
            201: openapi.Response(
                description="Review created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            400: openapi.Response(description="Bad request - validation error")
        }
    )
    def create(self, request, *args, **kwargs):
        # Set the product_id from URL
        data = request.data.copy()
        data['product'] = self.kwargs.get('product_id')
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            review = serializer.save()
            return Response({
                'success': True,
                'message': 'Review created successfully',
                'data': ReviewSerializer(review).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Review creation failed',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a review.
    Users can only update/delete their own reviews.
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ReviewCreateSerializer
        return ReviewSerializer
    
    @swagger_auto_schema(
        operation_description="Get a specific review",
        responses={
            200: openapi.Response(
                description="Review retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            404: openapi.Response(description="Review not found")
        }
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'message': 'Review retrieved successfully',
            'data': serializer.data
        })
    
    @swagger_auto_schema(
        operation_description="Update a review (only review author can update)",
        request_body=ReviewCreateSerializer,
        responses={
            200: openapi.Response(
                description="Review updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            403: openapi.Response(description="Forbidden - not the review author")
        }
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if user is the review author
        if instance.user != request.user and not request.user.is_admin:
            return Response({
                'success': False,
                'message': 'You can only update your own reviews'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            review = serializer.save()
            return Response({
                'success': True,
                'message': 'Review updated successfully',
                'data': ReviewSerializer(review).data
            })
        
        return Response({
            'success': False,
            'message': 'Review update failed',
            'data': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Delete a review (only review author can delete)",
        responses={
            200: openapi.Response(
                description="Review deleted successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            403: openapi.Response(description="Forbidden - not the review author")
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if user is the review author
        if instance.user != request.user and not request.user.is_admin:
            return Response({
                'success': False,
                'message': 'You can only delete your own reviews'
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance.delete()
        return Response({
            'success': True,
            'message': 'Review deleted successfully'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@swagger_auto_schema(
    operation_description="Mark a review as helpful",
    responses={
        200: openapi.Response(
            description="Review marked as helpful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'helpful_votes': openapi.Schema(type=openapi.TYPE_INTEGER)
                        }
                    )
                }
            )
        ),
        404: openapi.Response(description="Review not found")
    }
)
def mark_review_helpful(request, review_id):
    """
    Mark a review as helpful (increment helpful_votes).
    """
    try:
        review = Review.objects.get(id=review_id)
        review.helpful_votes += 1
        review.save()
        
        return Response({
            'success': True,
            'message': 'Review marked as helpful',
            'data': {
                'helpful_votes': review.helpful_votes
            }
        })
    except Review.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Review not found'
        }, status=status.HTTP_404_NOT_FOUND)


# Category Views
class CategoryListCreateView(generics.ListCreateAPIView):
    """
    List all categories or create a new category (Admin only for create)
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Category.objects.none()
        
        # Only show active categories to non-admin users
        if self.request.user.is_admin:
            return Category.objects.all()
        return Category.objects.filter(is_active=True)
    
    @swagger_auto_schema(
        operation_description="Get all categories",
        responses={
            200: openapi.Response(
                description="Categories retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT))
                    }
                )
            )
        }
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return Response({
            'success': True,
            'message': 'Categories retrieved successfully',
            'data': serializer.data
        })
    
    @swagger_auto_schema(
        operation_description="Create a new category (Admin only)",
        request_body=CategorySerializer,
        responses={
            201: openapi.Response(
                description="Category created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            403: openapi.Response(description="Only admins can create categories")
        }
    )
    def create(self, request, *args, **kwargs):
        # Only admins can create categories
        if not request.user.is_admin:
            return Response({
                'success': False,
                'message': 'Only admins can create categories'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response({
            'success': True,
            'message': 'Category created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a category (Admin only for update/delete)
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Category.objects.none()
        return Category.objects.all()
    
    @swagger_auto_schema(
        operation_description="Get a specific category",
        responses={
            200: openapi.Response(
                description="Category retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            404: openapi.Response(description="Category not found")
        }
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        
        return Response({
            'success': True,
            'message': 'Category retrieved successfully',
            'data': serializer.data
        })
    
    @swagger_auto_schema(
        operation_description="Update a category (Admin only)",
        request_body=CategorySerializer,
        responses={
            200: openapi.Response(
                description="Category updated successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            403: openapi.Response(description="Only admins can update categories")
        }
    )
    def update(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response({
                'success': False,
                'message': 'Only admins can update categories'
            }, status=status.HTTP_403_FORBIDDEN)
        
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Category updated successfully',
            'data': serializer.data
        })
    
    @swagger_auto_schema(
        operation_description="Delete a category (Admin only)",
        responses={
            200: openapi.Response(
                description="Category deleted successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(description="Cannot delete category with existing products"),
            403: openapi.Response(description="Only admins can delete categories")
        }
    )
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return Response({
                'success': False,
                'message': 'Only admins can delete categories'
            }, status=status.HTTP_403_FORBIDDEN)
        
        instance = self.get_object()
        
        # Check if any products are using this category
        product_count = Product.objects.filter(category=instance.name).count()
        if product_count > 0:
            return Response({
                'success': False,
                'message': f'Cannot delete category. {product_count} products are using this category.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        self.perform_destroy(instance)
        
        return Response({
            'success': True,
            'message': 'Category deleted successfully'
        }, status=status.HTTP_200_OK)
