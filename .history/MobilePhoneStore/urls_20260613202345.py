from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('products', include('products.urls')),
    
]

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 1. Admin panel
    path('admin/', admin.site.urls),

    # 2. Your homepage (Fixes the empty path error)
    # Option A: If your views are in the same folder
    # path('', views.home, name='home'), 
    # Option B: If you want to redirect or use an app's URLs
    # path('', include('your_app_name.urls')), 

    # 3. Your product detail path
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
]

# 4. Your media helper (Keep this at the very bottom)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

