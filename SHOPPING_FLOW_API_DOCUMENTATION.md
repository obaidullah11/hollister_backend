# Shopping Flow API Documentation

## Overview

This document provides complete API documentation for the Holister Admin shopping flow, including product browsing, cart management, and order placement.

## Base URL
```
http://localhost:8000/api/
```

## Authentication
All endpoints require JWT authentication. Include the following header in all requests:
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

---

## Complete Shopping Flow

### Step 1: User Browses Products

#### 1.1 Get All Products
```http
GET /api/products/products/
```

**Response:**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Classic Cotton T-Shirt",
            "sku": "TSH-001",
            "description": "Comfortable cotton t-shirt",
            "selling_price": "29.99",
            "category": "Clothing",
            "brand": "Holister",
            "images": [
                {
                    "id": 1,
                    "image_url": "https://example.com/image1.jpg"
                }
            ],
            "variants": [
                {
                    "id": 1,
                    "name": "Blue",
                    "color": "#0000FF",
                    "sizes": [
                        {
                            "id": 1,
                            "size": "S",
                            "stock": 10
                        },
                        {
                            "id": 2,
                            "size": "M",
                            "stock": 15
                        }
                    ]
                }
            ]
        }
    ]
}
```

#### 1.2 Get Single Product Details
```http
GET /api/products/products/1/
```

**Response:**
```json
{
    "id": 1,
    "name": "Classic Cotton T-Shirt",
    "sku": "TSH-001",
    "description": "Comfortable cotton t-shirt",
    "selling_price": "29.99",
    "category": "Clothing",
    "brand": "Holister",
    "images": [...],
    "variants": [...],
    "created_at": "2025-08-12T18:45:40Z",
    "updated_at": "2025-08-12T18:45:40Z"
}
```

---

### Step 2: Add Product to Cart

#### 2.1 Add Product to Cart
```http
POST /api/orders/cart/add/
```

**Request Body Examples:**

**Basic Product (No Variant/Size):**
```json
{
    "product_id": 1,
    "quantity": 2
}
```

**Product with Variant:**
```json
{
    "product_id": 1,
    "variant_id": 2,
    "quantity": 1
}
```

**Product with Variant and Size:**
```json
{
    "product_id": 1,
    "variant_id": 2,
    "size_id": 3,
    "quantity": 2
}
```

**Response:**
```json
{
    "success": true,
    "message": "Item added to cart successfully",
    "data": {
        "id": 1,
        "items": [
            {
                "id": 1,
                "product": {
                    "id": 1,
                    "name": "Classic Cotton T-Shirt",
                    "sku": "TSH-001",
                    "selling_price": "29.99",
                    "category": "Clothing"
                },
                "variant": {
                    "id": 2,
                    "name": "Blue",
                    "color": "#0000FF"
                },
                "size": {
                    "id": 3,
                    "size": "M",
                    "stock": 15
                },
                "quantity": 2,
                "unit_price": "29.99",
                "total_price": "59.98",
                "created_at": "2025-08-12T18:45:40Z"
            }
        ],
        "total_items": 2,
        "total_amount": "59.98",
        "created_at": "2025-08-12T18:45:40Z",
        "updated_at": "2025-08-12T18:45:40Z"
    }
}
```

---

### Step 3: Cart Updates Automatically

#### 3.1 View Current Cart
```http
GET /api/orders/cart/
```

**Response:**
```json
{
    "id": 1,
    "items": [
        {
            "id": 1,
            "product": {
                "id": 1,
                "name": "Classic Cotton T-Shirt",
                "sku": "TSH-001",
                "selling_price": "29.99",
                "category": "Clothing"
            },
            "variant": {
                "id": 2,
                "name": "Blue",
                "color": "#0000FF"
            },
            "size": {
                "id": 3,
                "size": "M",
                "stock": 15
            },
            "quantity": 2,
            "unit_price": "29.99",
            "total_price": "59.98"
        },
        {
            "id": 2,
            "product": {
                "id": 2,
                "name": "Denim Jeans",
                "sku": "JNS-001",
                "selling_price": "79.99",
                "category": "Clothing"
            },
            "variant": {
                "id": 5,
                "name": "Dark Blue",
                "color": "#000080"
            },
            "size": {
                "id": 8,
                "size": "32",
                "stock": 8
            },
            "quantity": 1,
            "unit_price": "79.99",
            "total_price": "79.99"
        }
    ],
    "total_items": 3,
    "total_amount": "139.97",
    "created_at": "2025-08-12T18:45:40Z",
    "updated_at": "2025-08-12T18:45:40Z"
}
```

#### 3.2 Update Cart Item Quantity
```http
PUT /api/orders/cart/update/1/
```

**Request Body:**
```json
{
    "quantity": 3
}
```

**Response:**
```json
{
    "success": true,
    "message": "Cart item updated successfully",
    "data": {
        "id": 1,
        "items": [...],
        "total_items": 4,
        "total_amount": "169.96",
        "created_at": "2025-08-12T18:45:40Z",
        "updated_at": "2025-08-12T18:45:40Z"
    }
}
```

#### 3.3 Remove Item from Cart
```http
DELETE /api/orders/cart/remove/2/
```

**Response:**
```json
{
    "success": true,
    "message": "Item removed from cart successfully",
    "data": {
        "id": 1,
        "items": [...],
        "total_items": 3,
        "total_amount": "89.97",
        "created_at": "2025-08-12T18:45:40Z",
        "updated_at": "2025-08-12T18:45:40Z"
    }
}
```

#### 3.4 Clear Entire Cart
```http
DELETE /api/orders/cart/clear/
```

**Response:**
```json
{
    "success": true,
    "message": "Cart cleared successfully",
    "data": {
        "id": 1,
        "items": [],
        "total_items": 0,
        "total_amount": "0.00",
        "created_at": "2025-08-12T18:45:40Z",
        "updated_at": "2025-08-12T18:45:40Z"
    }
}
```

---

### Step 4: User Reviews Cart and Proceeds to Checkout

#### 4.1 Final Cart Review
```http
GET /api/orders/cart/
```

**Response (Final Review):**
```json
{
    "id": 1,
    "items": [
        {
            "id": 1,
            "product": {
                "id": 1,
                "name": "Classic Cotton T-Shirt",
                "sku": "TSH-001",
                "selling_price": "29.99",
                "category": "Clothing"
            },
            "variant": {
                "id": 2,
                "name": "Blue",
                "color": "#0000FF"
            },
            "size": {
                "id": 3,
                "size": "M",
                "stock": 15
            },
            "quantity": 3,
            "unit_price": "29.99",
            "total_price": "89.97"
        }
    ],
    "total_items": 3,
    "total_amount": "89.97",
    "created_at": "2025-08-12T18:45:40Z",
    "updated_at": "2025-08-12T18:45:40Z"
}
```

---

### Step 5: Fill Shipping/Billing Information

#### 5.1 Get User's Saved Shipping Addresses
```http
GET /api/orders/shipping-addresses/
```

**Response:**
```json
[
    {
        "id": 1,
        "address_line_1": "123 Main Street",
        "address_line_2": "Apt 4B",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "United States",
        "is_default": true,
        "created_at": "2025-08-12T18:45:40Z"
    },
    {
        "id": 2,
        "address_line_1": "456 Oak Avenue",
        "address_line_2": "",
        "city": "Los Angeles",
        "state": "CA",
        "postal_code": "90210",
        "country": "United States",
        "is_default": false,
        "created_at": "2025-08-12T18:45:40Z"
    }
]
```

#### 5.2 Create New Shipping Address
```http
POST /api/orders/shipping-addresses/
```

**Request Body:**
```json
{
    "address_line_1": "789 Pine Street",
    "address_line_2": "Suite 100",
    "city": "Chicago",
    "state": "IL",
    "postal_code": "60601",
    "country": "United States",
    "is_default": false
}
```

**Response:**
```json
{
    "id": 3,
    "address_line_1": "789 Pine Street",
    "address_line_2": "Suite 100",
    "city": "Chicago",
    "state": "IL",
    "postal_code": "60601",
    "country": "United States",
    "is_default": false,
    "created_at": "2025-08-12T18:45:40Z"
}
```

---

### Step 6: Confirm Order Placement (Checkout)

#### 6.1 Process Checkout
```http
POST /api/orders/checkout/
```

**Request Body Examples:**

**Same Shipping and Billing Address:**
```json
{
    "email": "customer@example.com",
    "phone_number": "+1234567890",
    "shipping_address": {
        "address_line_1": "123 Main Street",
        "address_line_2": "Apt 4B",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "United States"
    },
    "notes": "Please deliver after 6 PM"
}
```

**Different Billing Address:**
```json
{
    "email": "customer@example.com",
    "phone_number": "+1234567890",
    "shipping_address": {
        "address_line_1": "123 Main Street",
        "address_line_2": "Apt 4B",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country": "United States"
    },
    "billing_address": {
        "address_line_1": "456 Business Ave",
        "address_line_2": "Floor 10",
        "city": "New York",
        "state": "NY",
        "postal_code": "10002",
        "country": "United States"
    },
    "notes": "Business delivery"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Order placed successfully",
    "data": {
        "order": {
            "id": 1,
            "order_number": "ORD-A1B2C3D4",
            "customer": {
                "id": 1,
                "email": "customer@example.com",
                "first_name": "John",
                "last_name": "Doe"
            },
            "status": "pending",
            "payment_status": "completed",
            "total_amount": "89.97",
            "email": "customer@example.com",
            "phone_number": "+1234567890",
            "shipping_address": {
                "id": 4,
                "address_line_1": "123 Main Street",
                "address_line_2": "Apt 4B",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "United States"
            },
            "billing_address": {
                "id": 5,
                "address_line_1": "123 Main Street",
                "address_line_2": "Apt 4B",
                "city": "New York",
                "state": "NY",
                "postal_code": "10001",
                "country": "United States"
            },
            "notes": "Please deliver after 6 PM",
            "items": [
                {
                    "id": 1,
                    "product": {
                        "id": 1,
                        "name": "Classic Cotton T-Shirt",
                        "sku": "TSH-001"
                    },
                    "variant": {
                        "id": 2,
                        "name": "Blue",
                        "color": "#0000FF"
                    },
                    "size": {
                        "id": 3,
                        "size": "M"
                    },
                    "quantity": 3,
                    "unit_price": "29.99",
                    "total_price": "89.97"
                }
            ],
            "created_at": "2025-08-12T18:45:40Z",
            "updated_at": "2025-08-12T18:45:40Z"
        },
        "order_number": "ORD-A1B2C3D4"
    }
}
```

---

### Step 7: Receive Order Confirmation

#### 7.1 View Order Details
```http
GET /api/orders/orders/1/
```

**Response:**
```json
{
    "id": 1,
    "order_number": "ORD-A1B2C3D4",
    "customer": {
        "id": 1,
        "email": "customer@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "status": "pending",
    "payment_status": "completed",
    "total_amount": "89.97",
    "email": "customer@example.com",
    "phone_number": "+1234567890",
    "shipping_address": {...},
    "billing_address": {...},
    "notes": "Please deliver after 6 PM",
    "items": [...],
    "status_history": [
        {
            "id": 1,
            "status": "pending",
            "notes": "Order placed successfully",
            "created_by": {
                "id": 1,
                "email": "customer@example.com"
            },
            "created_at": "2025-08-12T18:45:40Z"
        }
    ],
    "created_at": "2025-08-12T18:45:40Z",
    "updated_at": "2025-08-12T18:45:40Z"
}
```

#### 7.2 View All Customer Orders
```http
GET /api/orders/orders/
```

**Response:**
```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "order_number": "ORD-A1B2C3D4",
            "status": "pending",
            "total_amount": "89.97",
            "created_at": "2025-08-12T18:45:40Z"
        }
    ]
}
```

---

## Error Responses

### Cart Empty Error
```json
{
    "success": false,
    "message": "Cart is empty"
}
```

### Insufficient Stock Error
```json
{
    "success": false,
    "message": "Only 5 units available in stock"
}
```

### Invalid Address Error
```json
{
    "success": false,
    "message": "Invalid checkout data",
    "errors": {
        "shipping_address": {
            "city": ["This field is required."]
        }
    }
}
```

### Authentication Error
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### Product Not Found Error
```json
{
    "success": false,
    "message": "Failed to add item to cart",
    "errors": {
        "product_id": ["Product not found"]
    }
}
```

---

## Order Status Reference

### Order Statuses
- `pending` - Order placed, awaiting confirmation
- `confirmed` - Order confirmed by admin
- `processing` - Order being prepared
- `shipped` - Order shipped to customer
- `delivered` - Order delivered successfully
- `cancelled` - Order cancelled
- `refunded` - Order refunded

### Payment Statuses
- `pending` - Payment pending
- `completed` - Payment completed
- `failed` - Payment failed
- `refunded` - Payment refunded

---

## Complete Flow Summary

| Step | Action | HTTP Method | Endpoint | Description |
|------|--------|-------------|----------|-------------|
| 1 | Browse Products | GET | `/api/products/products/` | Get all available products |
| 2 | Add to Cart | POST | `/api/orders/cart/add/` | Add product to shopping cart |
| 3 | View Cart | GET | `/api/orders/cart/` | View current cart contents |
| 4 | Update Cart | PUT | `/api/orders/cart/update/{id}/` | Update item quantity |
| 5 | Manage Addresses | GET/POST | `/api/orders/shipping-addresses/` | Get/create shipping addresses |
| 6 | Checkout | POST | `/api/orders/checkout/` | Process order and create order |
| 7 | Order Confirmation | GET | `/api/orders/orders/{id}/` | View order details |

---

## Additional Endpoints

### Cart Management
- `DELETE /api/orders/cart/remove/{id}/` - Remove specific item from cart
- `DELETE /api/orders/cart/clear/` - Clear entire cart

### Order Management
- `GET /api/orders/orders/` - List all customer orders
- `PUT /api/orders/orders/{id}/` - Update order details
- `DELETE /api/orders/orders/{id}/` - Cancel order

### Address Management
- `GET /api/orders/shipping-addresses/{id}/` - Get specific address
- `PUT /api/orders/shipping-addresses/{id}/` - Update address
- `DELETE /api/orders/shipping-addresses/{id}/` - Delete address

---

## Testing the API

### Using cURL Examples

#### 1. Get Products
```bash
curl -X GET "http://localhost:8000/api/products/products/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 2. Add to Cart
```bash
curl -X POST "http://localhost:8000/api/orders/cart/add/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "variant_id": 2,
    "size_id": 3,
    "quantity": 2
  }'
```

#### 3. View Cart
```bash
curl -X GET "http://localhost:8000/api/orders/cart/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

#### 4. Checkout
```bash
curl -X POST "http://localhost:8000/api/orders/checkout/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "phone_number": "+1234567890",
    "shipping_address": {
      "address_line_1": "123 Main Street",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "United States"
    }
  }'
```

---

## Notes

- All endpoints require JWT authentication
- Stock validation is performed automatically
- Cart items are unique by product + variant + size combination
- Order numbers are automatically generated (format: ORD-XXXXXXXX)
- Cart is automatically cleared after successful checkout
- All monetary values are returned as strings to preserve decimal precision
- Timestamps are in ISO 8601 format (UTC)
