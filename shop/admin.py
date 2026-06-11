from django.contrib import admin
# Добавили импорт Order и OrderItem
from .models import Category, Manufacturer, Product, Cart, CartItem, Profile, Order, OrderItem 

admin.site.register(Category)
admin.site.register(Manufacturer)
admin.site.register(Product)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total_price')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'item_total_price')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone')
    search_fields = ('user__username', 'full_name')

# --- Добавьте этот блок для заказов ---
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'is_paid')
    list_filter = ('is_paid', 'created_at')
    search_fields = ('user__username',)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')