# Shopping Flow API Endpoints

This document describes all the shopping flow endpoints available in the orders app.

## Shopping Flow Tag

All shopping-related endpoints are grouped under the **"Shopping Flow"** tag in Swagger documentation.

## Cart Endpoints

### 1. Get Cart
- **URL:** `GET /api/orders/cart/`
- **Description:** Retrieve the current user's shopping cart with all items
- **Authentication:** Required
- **Response:** Cart object with items, total_items, and total_amount

### 2. Add to Cart
- **URL:** `POST /api/orders/cart/add/`
- **Description:** Add a product to the user's shopping cart
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "product_id": 1,
    "variant_id": 2,  // optional
    "size_id": 3,     // optional
    "quantity": 1
  }
  ```
- **Response:** Updated cart object

### 3. Update Cart Item
- **URL:** `PUT/PATCH /api/orders/cart/update/{cart_item_id}/`
- **Description:** Update the quantity of a specific item in the user's cart
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "quantity": 2
  }
  ```
- **Response:** Updated cart object

### 4. Remove from Cart
- **URL:** `DELETE /api/orders/cart/remove/{cart_item_id}/`
- **Description:** Remove a specific item from the user's shopping cart
- **Authentication:** Required
- **Response:** Updated cart object

### 5. Clear Cart
- **URL:** `DELETE /api/orders/cart/clear/`
- **Description:** Remove all items from the user's shopping cart
- **Authentication:** Required
- **Response:** Empty cart object

## Checkout Endpoints

### 6. Checkout
- **URL:** `POST /api/orders/checkout/`
- **Description:** Process the checkout by creating an order from the user's cart items
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "phone_number": "+1234567890",
    "shipping_address": {
      "address_line_1": "123 Main St",
      "address_line_2": "Apt 4B",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "United States"
    },
    "billing_address": {  // optional, uses shipping_address if not provided
      "address_line_1": "123 Main St",
      "address_line_2": "Apt 4B",
      "city": "New York",
      "state": "NY",
      "postal_code": "10001",
      "country": "United States"
    },
    "notes": "Please deliver after 6 PM"  // optional
  }
  ```
- **Response:** Order object with order_number

## Shipping Address Endpoints

### 7. List Shipping Addresses
- **URL:** `GET /api/orders/shipping-addresses/`
- **Description:** List all shipping addresses for the current user
- **Authentication:** Required
- **Response:** Array of shipping address objects

### 8. Create Shipping Address
- **URL:** `POST /api/orders/shipping-addresses/`
- **Description:** Create a new shipping address for the current user
- **Authentication:** Required
- **Request Body:**
  ```json
  {
    "address_line_1": "123 Main St",
    "address_line_2": "Apt 4B",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "United States",
    "is_default": false
  }
  ```
- **Response:** Created shipping address object

### 9. Get Shipping Address
- **URL:** `GET /api/orders/shipping-addresses/{address_id}/`
- **Description:** Get a specific shipping address
- **Authentication:** Required
- **Response:** Shipping address object

### 10. Update Shipping Address
- **URL:** `PUT/PATCH /api/orders/shipping-addresses/{address_id}/`
- **Description:** Update a shipping address
- **Authentication:** Required
- **Request Body:** Same as create
- **Response:** Updated shipping address object

### 11. Delete Shipping Address
- **URL:** `DELETE /api/orders/shipping-addresses/{address_id}/`
- **Description:** Delete a shipping address
- **Authentication:** Required
- **Response:** 204 No Content

## Order Endpoints

### 12. List Orders (Customer)
- **URL:** `GET /api/orders/orders/`
- **Description:** List all orders for the current user
- **Authentication:** Required
- **Response:** Array of order objects

### 13. Get Order Details (Customer)
- **URL:** `GET /api/orders/orders/{order_id}/`
- **Description:** Get details of a specific order
- **Authentication:** Required
- **Response:** Order object with items and addresses

## Admin Order Endpoints

### 14. List Orders (Admin)
- **URL:** `GET /api/orders/admin/orders/`
- **Description:** List all orders (admin only)
- **Authentication:** Required (Admin)
- **Query Parameters:**
  - `status`: Filter by order status
  - `payment_status`: Filter by payment status
  - `search`: Search by order number or customer email
- **Response:** Array of order objects

### 15. Get Order Details (Admin)
- **URL:** `GET /api/orders/admin/orders/{order_id}/`
- **Description:** Get details of a specific order (admin only)
- **Authentication:** Required (Admin)
- **Response:** Order object with items and addresses

### 16. Update Order (Admin)
- **URL:** `PUT/PATCH /api/orders/admin/orders/{order_id}/`
- **Description:** Update order status and details (admin only)
- **Authentication:** Required (Admin)
- **Request Body:**
  ```json
  {
    "status": "processing",
    "payment_status": "completed"
  }
  ```
- **Response:** Updated order object

## Features

### Cart Features
- ✅ Add products to cart with variants and sizes
- ✅ Update item quantities
- ✅ Remove individual items
- ✅ Clear entire cart
- ✅ Stock validation
- ✅ Automatic price calculation

### Checkout Features
- ✅ Create orders from cart items
- ✅ Generate unique order numbers
- ✅ Create shipping and billing addresses
- ✅ Stock reduction on checkout
- ✅ Cart clearing after successful order
- ✅ Order status history tracking
- ✅ Default payment status as "completed"

### Order Management
- ✅ Customer order history
- ✅ Admin order management
- ✅ Order status updates
- ✅ Payment status tracking
- ✅ Address management
- ✅ Order filtering and search

### Security Features
- ✅ Authentication required for all endpoints
- ✅ User-specific cart and order access
- ✅ Admin-only access for admin endpoints
- ✅ Stock validation to prevent overselling

## Response Format

All endpoints follow a consistent response format:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data
  }
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (admin access required)
- `404`: Not Found
- `500`: Internal Server Error

## Swagger Documentation

All endpoints are documented in Swagger with:
- Detailed descriptions
- Request/response schemas
- Authentication requirements
- Example requests and responses
- Grouped under "Shopping Flow" tag
