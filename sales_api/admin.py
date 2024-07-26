from django.contrib import admin
from .models import Customer, Product, Sale

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'quantity', 'total_price', 'sale_date')
    list_filter = ('sale_date',)
    search_fields = ('customer__first_name', 'customer__last_name', 'product__name')

