# Holister Admin Backend

A Django REST API backend for the Holister Admin Panel with support for both Customer and Admin roles.

## Features

- **Authentication & Authorization**: JWT-based authentication with role-based access control
- **User Management**: Customer and Admin user management with profile management
- **Product Management**: Complete product catalog with variants, sizes, and images
- **Order Management**: Order processing with status tracking and history
- **Admin Dashboard**: Analytics and statistics for admin users
- **API Documentation**: Swagger/OpenAPI documentation
- **CORS Support**: Cross-origin resource sharing for frontend integration

## Technology Stack

- **Django 5.2.5**: Web framework
- **Django REST Framework**: API framework
- **SimpleJWT**: JWT authentication
- **Pillow**: Image processing
- **drf-yasg**: Swagger documentation
- **django-filter**: Advanced filtering
- **django-cors-headers**: CORS support

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django_backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication

- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/token/verify/` - Verify JWT token

### Accounts

- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/login/` - User login
- `POST /api/accounts/logout/` - User logout
- `GET /api/accounts/profile/` - Get user profile
- `PUT /api/accounts/profile/update/` - Update user profile

### Products

- `GET /api/products/products/` - List products
- `POST /api/products/products/create/` - Create product
- `GET /api/products/products/{id}/` - Get product details
- `PUT /api/products/products/{id}/` - Update product
- `DELETE /api/products/products/{id}/` - Delete product

### Orders

- `GET /api/orders/orders/` - List orders
- `POST /api/orders/orders/create/` - Create order
- `GET /api/orders/orders/{id}/` - Get order details
- `PUT /api/orders/orders/{id}/status/` - Update order status

### Admin Endpoints

- `GET /api/accounts/admin/users/` - List all users (Admin only)
- `GET /api/accounts/admin/dashboard-stats/` - Dashboard statistics (Admin only)
- `GET /api/products/admin/products/` - Admin product list (Admin only)
- `GET /api/products/admin/product-stats/` - Product statistics (Admin only)
- `GET /api/orders/admin/orders/` - Admin order list (Admin only)
- `GET /api/orders/admin/order-stats/` - Order statistics (Admin only)

## API Documentation

### Swagger UI
Visit `http://localhost:8000/swagger/` for interactive API documentation.

### ReDoc
Visit `http://localhost:8000/redoc/` for alternative API documentation.

## User Roles

### Customer
- View products
- Place orders
- Manage profile
- View order history

### Admin
- All customer permissions
- Manage users
- Manage products
- Manage orders
- View analytics and statistics
- Access admin dashboard

## Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Database

The project uses SQLite by default. For production, consider using PostgreSQL or MySQL.

## Media Files

Product images and user profile pictures are stored in the `media/` directory. Make sure the directory is writable.

## Testing

```bash
python manage.py test
```

## Production Deployment

1. Set `DEBUG=False` in settings
2. Configure a production database
3. Set up static file serving
4. Configure environment variables
5. Set up HTTPS
6. Configure CORS settings for your domain

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License
