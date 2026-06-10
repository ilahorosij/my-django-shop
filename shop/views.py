from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Product, Cart, CartItem, Category, Manufacturer
from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from openpyxl import Workbook
from io import BytesIO
from rest_framework import viewsets
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    ManufacturerSerializer,
    CartSerializer,
    CartItemSerializer
)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all()
    serializer_class = ManufacturerSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    
def home(request):
    
    products = Product.objects.all().order_by('-id')[:6]
    categories = Category.objects.all()
    return render(request, 'index.html', {
        'products': products,
        'categories': categories
    })

def author(request):
    return render(request, 'author.html')

def about(request):
    return render(request, 'about.html')


def product_list(request):
    """Список товаров с фильтрацией, поиском и пагинацией"""
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
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'products': page_obj,
        'categories': Category.objects.all(),
        'manufacturers': Manufacturer.objects.all(),
    }
    return render(request, 'product_list.html', context)


def product_detail(request, pk):
    """Детальная страница товара"""
    product = get_object_or_404(Product, pk=pk)
    context = {'product': product}
    return render(request, 'product_detail.html', context)



@login_required(login_url='/admin/login/')
def add_to_cart(request, product_id):
    """Добавить товар в корзину"""
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product
    )
    
    if not created:
        cart_item.quantity += 1
    else:
        cart_item.quantity = 1
    
    if cart_item.quantity > product.stock:
        messages.error(request, f'На складе только {product.stock} шт.')
        return redirect('shop:cart')  
    
    cart_item.save()
    messages.success(request, f'{product.name} добавлен в корзину')
    return redirect('shop:cart')


@login_required
def update_cart(request, item_id):
    """Обновить количество товара в корзине"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    if request.method == 'POST':
        try:
            new_qty = int(request.POST.get('quantity', 1))
            if new_qty < 1:
                messages.error(request, 'Минимум 1 штука')
            elif new_qty > cart_item.product.stock:
                messages.error(request, f'На складе только {cart_item.product.stock} шт.')
            else:
                cart_item.quantity = new_qty
                cart_item.save()
                messages.success(request, 'Обновлено')
        except (ValueError, TypeError):
            messages.error(request, 'Некорректное количество')
    
    return redirect('shop:cart')


@login_required
def remove_from_cart(request, item_id):
    """Удалить товар из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} удалён из корзины')
    return redirect('shop:cart')


@login_required
def cart_view(request):
    """Страница корзины"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if created:
        cart_items = []
        total_price = 0
    else:
        cart_items = cart.cart_items.select_related('product').all()
        total_price = cart.total_price  
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)

@login_required
def checkout_success(request):
    return render(request, "checkout_success.html")

@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_items = cart.cart_items.select_related('product')
    if request.method == "GET":
        return render(request, "checkout.html", {
            "cart": cart,
            "items": cart_items
        })

    if request.method == "POST":

        try:
            selected_items = request.POST.getlist("items")

            if not selected_items:
                messages.error(request, "Выберите товары для заказа")
                return redirect("shop:cart")

            items = CartItem.objects.filter(
                id__in=selected_items,
                cart=cart
            ).select_related('product')

            if not items.exists():
                messages.error(request, "Товары не найдены")
                return redirect("shop:cart")

            address = request.POST.get("address")

            if not address:
                messages.error(request, "Введите адрес доставки")
                return redirect("shop:cart")

            wb = Workbook()
            ws = wb.active
            ws.title = "Чек заказа"

            ws.append(["Товар", "Цена", "Кол-во", "Сумма"])

            total = 0

            for item in items:
                sum_item = item.product.price * item.quantity
                total += sum_item

                ws.append([
                    item.product.name,
                    float(item.product.price),
                    item.quantity,
                    float(sum_item)
                ])

            ws.append([])
            ws.append(["ИТОГО", "", "", total])
            ws.append(["Адрес:", address])

            file = BytesIO()
            wb.save(file)
            file.seek(0)

            email = EmailMessage(
                subject="Ваш заказ",
                body=f"Спасибо за заказ!\nАдрес: {address}",
                to=[request.user.email or "test@mail.com"],
            )

            email.attach(
                "check.xlsx",
                file.read(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            email.send(fail_silently=False)

            items.delete()

            messages.success(request, "Заказ успешно оформлен!")

            return redirect("shop:checkout_success")

        except Exception as e:
            messages.error(request, f"Ошибка оформления заказа: {e}")
            return redirect("shop:checkout")