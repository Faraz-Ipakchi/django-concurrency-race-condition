from django.contrib import admin
from django.urls import path
from shop import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/products/<int:pk>/purchase-naive/', views.purchase_naive),
    path('api/products/<int:pk>/purchase-atomic/', views.purchase_atomic_only),
    path('api/products/<int:pk>/purchase-lock/', views.purchase_with_lock),
    path('api/products/<int:pk>/purchase-f/', views.purchase_atomic_f_update),
]