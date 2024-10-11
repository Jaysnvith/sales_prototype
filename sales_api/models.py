from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Sale(models.Model):
    CATEGORY_CHOICES = [
        ('aftermarket', 'Aftermarket'),
        ('export', 'Export'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='aftermarket')

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale of {self.product.name} to {self.customer.first_name} {self.customer.last_name} on {self.sale_date}"

# Auto update total price
@receiver(post_save, sender=Product)
def update_sale_total_price(sender, instance, created, **kwargs):
    if not created:  # Skip if the product instance is being created for the first time
        # Update all related Sale instances' total_price
        sales = Sale.objects.filter(product=instance)
        for sale in sales:
            sale.total_price = sale.product.price * sale.quantity
            sale.save()