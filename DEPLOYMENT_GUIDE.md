# Swagger Documentation Deployment Guide

## Issues Fixed

### 1. **Production Settings Configuration**
- Added `SWAGGER_SETTINGS` and `REDOC_SETTINGS` for better production support
- Configured proper static files handling
- Added security definitions for Bearer token authentication

### 2. **URL Configuration Updates**
- Added explicit patterns to schema view for better endpoint discovery
- Added alternative OpenAPI endpoints for production compatibility
- Multiple fallback URLs for different deployment scenarios

### 3. **Static Files Configuration**
- Proper `STATIC_URL` and `STATIC_ROOT` configuration
- Added `STATICFILES_DIRS` and `STATICFILES_FINDERS`

## Deployment Steps

### For PythonAnywhere (Current Deployment)

1. **Collect Static Files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

2. **Run Migrations:**
   ```bash
   python manage.py migrate
   ```

3. **Restart Your Web App:**
   - Go to your PythonAnywhere dashboard
   - Click "Reload" on your web app

### For Other Platforms (Heroku, Railway, etc.)

1. **Add to requirements.txt:**
   ```
   drf-yasg==1.21.7
   ```

2. **Set Environment Variables:**
   ```bash
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   ```

3. **Deploy:**
   ```bash
   git add .
   git commit -m "Fix Swagger production deployment"
   git push
   ```

## Testing Your Deployment

After deployment, test these URLs:

### Primary URLs:
- `https://your-domain.com/` - Main Swagger UI
- `https://your-domain.com/swagger/` - Swagger UI
- `https://your-domain.com/redoc/` - ReDoc UI

### Alternative URLs:
- `https://your-domain.com/api-docs/` - Alternative Swagger UI
- `https://your-domain.com/openapi.json` - Raw OpenAPI JSON
- `https://your-domain.com/swagger.json` - Swagger JSON

### API Endpoints:
- `https://your-domain.com/api/accounts/` - Accounts API
- `https://your-domain.com/api/products/` - Products API
- `https://your-domain.com/api/orders/` - Orders API

## Common Issues & Solutions

### Issue 1: "Schema not found" or 404 errors
**Solution:** Make sure you've run `collectstatic` and restarted your web app.

### Issue 2: Static files not loading
**Solution:** Check that `STATIC_ROOT` is properly configured and static files are collected.

### Issue 3: CORS errors in browser
**Solution:** Verify `CORS_ALLOWED_ORIGINS` includes your frontend domain.

### Issue 4: Authentication not working in Swagger
**Solution:** Use the "Authorize" button in Swagger UI and enter: `Bearer your-jwt-token`

## Environment Variables for Production

Create a `.env` file or set these environment variables:

```bash
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

## Verification Checklist

- [ ] Static files collected (`collectstatic` run)
- [ ] Web app restarted
- [ ] Environment variables set correctly
- [ ] `ALLOWED_HOSTS` includes your domain
- [ ] CORS settings configured for your frontend
- [ ] Database migrations applied
- [ ] All URLs accessible (test each one)

## Support

If you're still having issues:

1. Check your deployment platform's logs
2. Verify all environment variables are set
3. Test the OpenAPI JSON endpoint directly: `https://your-domain.com/openapi.json`
4. Check browser console for JavaScript errors
5. Verify static files are being served correctly

The Swagger documentation should now work properly in production! 🚀
