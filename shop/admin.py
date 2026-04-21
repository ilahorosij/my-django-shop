from django.contrib import admin
from .models import Category, Manufacturer, Product, Cart, CartItem
admin.site.register(Category)
admin.site.register(Manufacturer)
admin.site.register(Product)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total_price')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'item_total_price')