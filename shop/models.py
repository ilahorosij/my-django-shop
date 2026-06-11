from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.TextField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
class OrderItem(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес доставки")
    city = models.CharField(max_length=100, verbose_name="Город доставки", blank=True)
    favorite_category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Любимая категория")
    # Добавляем поле для чеков
    email_for_receipt = models.EmailField(verbose_name="Email для чеков", blank=True, null=True)

    def __str__(self):
        return f"Профиль {self.user.username}"
# Это нужно, чтобы профиль создавался САМ при регистрации
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)

def save_user_profile(sender, instance, **kwargs):
    # Добавляем проверку: если профиля нет, создаем его
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)
class Manufacturer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    country = models.CharField(max_length=100, verbose_name="Страна")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")

    def __str__(self):
        return self.name
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, null=True, verbose_name="Описание категории")

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание")

    
    photo = models.ImageField(
        upload_to='products/',  
        blank=True, 
        null=True,
        verbose_name="Фото"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0)], 
        verbose_name="Цена"
    )
    
    stock = models.IntegerField(
        validators=[MinValueValidator(0)], 
        verbose_name="Количество на складе"
    )

    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE, verbose_name="Производитель")

    def __str__(self):
        return self.name
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"

    @property
    def total_price(self):
        
        return sum(item.item_total_price() for item in self.cart_items.all())

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items", verbose_name="Корзина")
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return f"{self.product.name} ({self.quantity} шт.)"

    def item_total_price(self):
        return self.product.price * self.quantity

    def clean(self):
        
        if self.quantity > self.product.stock:
            raise ValidationError(
                f"Недостаточно товара на складе. Доступно: {self.product.stock}"
            )

    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"