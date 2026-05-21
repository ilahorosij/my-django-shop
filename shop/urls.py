from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    CategoryViewSet,
    ManufacturerViewSet,
    CartViewSet,
    CartItemViewSet
)

app_name = 'shop'  
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'manufacturers', ManufacturerViewSet)
router.register(r'cart', CartViewSet)
router.register(r'cart-items', CartItemViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('author/', views.author, name='author'),
    path('about/', views.about, name='about'),
    path('catalog/', views.product_list, name='catalog'),
    path('catalog/<int:pk>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('api/', include(router.urls)),
    
    
]
