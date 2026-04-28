from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'shop'  

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
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    
]
