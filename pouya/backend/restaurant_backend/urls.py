"""
URL configuration for restaurant_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from menu.views import CategoryViewSet, MenuItemViewSet, DailyInventoryViewSet
from orders.views import OrderViewSet, OrderItemViewSet, TableViewSet
from users.views import LoginView, LogoutView, RegisterView, ProfileView
from analytics.views import StatisticsView, PredictionsView

# Create router and register viewsets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'menu-items', MenuItemViewSet)
router.register(r'inventory', DailyInventoryViewSet)
router.register(r'tables', TableViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    
    # Authentication endpoints
    path('api/auth/login/', LoginView.as_view(), name='auth_login'),
    path('api/auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    path('api/auth/profile/', ProfileView.as_view(), name='auth_profile'),

    # Analytics endpoints (admin only)
    path('api/analytics/statistics/', StatisticsView.as_view(), name='analytics_statistics'),
    path('api/analytics/predictions/', PredictionsView.as_view(), name='analytics_predictions'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
