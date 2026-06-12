from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from django.core.paginator import Paginator
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from io import BytesIO
from .models import Order, OrderItem
from openpyxl import Workbook
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Product, Cart, CartItem, Category, Manufacturer
from .forms import RegistrationForm
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    ManufacturerSerializer,
    CartSerializer,
    CartItemSerializer,
    ProfileSerializer
)
from .permissions import IsAdminOrReadOnly

from .models import Order
from .serializers import OrderSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from rest_framework import status
from django.http import JsonResponse

def api_categories(request):
    # Берем все категории и превращаем в список словарей
    categories = list(Category.objects.values('id', 'name'))
    return JsonResponse(categories, safe=False)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"detail": "Неверный старый пароль"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            validate_password(new_password, user)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Пароль успешно изменен"})

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()

        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
# =========================
# DRF VIEWSETS
# =========================

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer
    permission_classes = [IsAdminOrReadOnly]

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()  # Добавьте эту строку
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

# =========================
# PROFILE API (ВАЖНО: ОТДЕЛЬНО!)
# =========================

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user.profile)
        return Response(serializer.data)

    def patch(self, request):
        serializer = ProfileSerializer(
            request.user.profile,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# =========================
# FRONTEND VIEWS
# =========================

def home(request):
    products = Product.objects.all().order_by('-id')[:6]
    categories = Category.objects.all()
    return render(request, 'index.html', {
        'products': products,
        'categories': categories
    })


def author(request):
    return render(request, 'author.html')

def profile_view(request):
    return render(request, 'profile.html')
def about(request):
    return render(request, 'about.html')


# =========================
# AUTH
# =========================

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('shop:home')
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('shop:home')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('shop:home')


# =========================
# PRODUCTS
# =========================

def product_list(request):
    products = Product.objects.select_related('category', 'manufacturer').all()

    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)

    manufacturer_id = request.GET.get('manufacturer')
    if manufacturer_id:
        products = products.filter(manufacturer_id=manufacturer_id)

    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    paginator = Paginator(products, 9)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'product_list.html', {
        'products': page_obj,
        'categories': Category.objects.all(),
        'manufacturers': Manufacturer.objects.all(),
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


# =========================
# CART
# =========================

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    item.quantity = item.quantity + 1 if not created else 1

    if item.quantity > product.stock:
        messages.error(request, f'На складе только {product.stock} шт.')
        return redirect('shop:cart')

    item.save()
    messages.success(request, f'{product.name} добавлен в корзину')
    return redirect('shop:cart')


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.cart_items.select_related('product').all()

    return render(request, 'cart.html', {
        'cart': cart,
        'cart_items': items,
        'total_price': cart.total_price
    })


@login_required
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == "POST":
        try:
            qty = int(request.POST.get("quantity", 1))

            if qty < 1:
                messages.error(request, "Минимум 1")
            elif qty > item.product.stock:
                messages.error(request, "Нет на складе")
            else:
                item.quantity = qty
                item.save()
                messages.success(request, "Обновлено")

        except ValueError:
            messages.error(request, "Ошибка количества")

    return redirect('shop:cart')


import resend
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from io import BytesIO
from openpyxl import Workbook
from .models import Cart, CartItem, Order, OrderItem

@login_required
def checkout(request):
    # 1. Получение профиля
    try:
        user_profile = request.user.profile
    except AttributeError:
        messages.error(request, "Профиль пользователя не найден.")
        return redirect("shop:home")

    target_email = getattr(user_profile, 'email_for_receipt', None) or request.user.email
    
    # 2. Валидация
    if not all([user_profile.full_name, user_profile.phone, user_profile.address, target_email]):
        messages.error(request, "Заполните профиль.")
        return redirect("shop:profile")

    cart, _ = Cart.objects.get_or_create(user=request.user)

    if request.method == "GET":
        items = cart.cart_items.select_related('product').all()
        if not items.exists():
            return redirect("shop:cart")
        return render(request, "checkout.html", {"cart": cart, "items": items})

    # 3. POST запрос (Оформление)
    selected_ids = request.POST.getlist("items")
    items = CartItem.objects.filter(id__in=selected_ids, cart=cart).select_related('product')
    
    if not items.exists():
        messages.error(request, "Выберите товары.")
        return redirect("shop:cart")

    # Создание заказа
    new_order = Order.objects.create(user=request.user, address=user_profile.address, is_paid=False)
    for item in items:
        OrderItem.objects.create(order=new_order, product=item.product, quantity=item.quantity, price=item.product.price)

    # 4. Генерация Excel
    wb = Workbook()
    ws = wb.active
    ws.append(["Товар", "Цена", "Кол-во", "Сумма"])
    total = 0
    for item in items:
        sum_item = item.product.price * item.quantity
        total += sum_item
        ws.append([item.product.name, float(item.product.price), item.quantity, float(sum_item)])
    ws.append(["ИТОГО", "", "", total])
    
    file = BytesIO()
    wb.save(file)
    file_bytes = file.getvalue() # Получаем байты
    file.close()

    # 5. Отправка через Resend API
    try:
        resend.api_key = settings.RESEND_API_KEY
        params = {
            "from": "onboarding@resend.dev",
            "to": "ilahorosij5822@gmail.com",
            "subject": f"Ваш заказ №{new_order.id}",
            "html": f"<h2>Спасибо за заказ!</h2><p>Ваш заказ №{new_order.id} оформлен.</p>",
            "attachments": [
                {
                    "filename": "order.xlsx",
                    "content": list(file_bytes) # Преобразуем в список для API
                }
            ]
        }
        resend.Emails.send(params)
        messages.success(request, "Заказ оформлен, информация отправлена на почту.")
    except Exception as e:
        print(f"Ошибка при отправке через Resend: {e}")
        messages.error(request, "Заказ оформлен, но возникла ошибка при отправке email.")
    
    # Очистка корзины после успешного оформления
    items.delete()
    return redirect("shop:home") # Или на страницу успеха
from django.shortcuts import redirect, get_object_or_404
from .models import CartItem # Импортируйте вашу модель корзины

def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('shop:cart') # Перенаправляем обратно в корзину
from django.shortcuts import render

def checkout_success(request):
    return render(request, 'checkout_success.html') 
    # Убедитесь, что у вас есть файл шаблона checkout_success.html 
    # в папке templates/shop/