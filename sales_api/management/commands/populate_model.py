from django.core.management.base import BaseCommand
from sales_api.models import Customer, Product, Sale
from faker import Faker
import random

class Command(BaseCommand):
    help = 'Populate the database with sample sales data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Create Customers
        customers = []
        for _ in range(20):
            customer = Customer(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                phone_number=fake.phone_number()[:15]
            )
            customer.save()
            customers.append(customer)
        
        # Create Products
        products = []
        for _ in range(20):
            product = Product(
                name=fake.word(),
                description=fake.text(),
                price=round(random.uniform(10.0, 100.0), 2)
            )
            product.save()
            products.append(product)
        
        # Create Sales
        for _ in range(20):
            sale = Sale(
                customer=random.choice(customers),
                product=random.choice(products),
                quantity=random.randint(1, 10)
            )
            sale.save()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated the database with sample sales data'))
