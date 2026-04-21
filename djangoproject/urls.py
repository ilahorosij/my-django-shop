from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # ← 1. Добавь этот импорт
from django.conf.urls.static import static  # ← 2. И этот

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),  # Подключаем твое приложение
]

# ← 3. В САМЫЙ НИЗ файла добавь этот блок:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)