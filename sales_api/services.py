import calendar
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from .models import Sale, Product, Customer

class SalesData:
    def __init__(self, month, year):
        self.month = month
        self.year = year
        self.previous_month = self.month - 1
        self.previous_year = self.year - 1 if month == 1 else self.year

    def get_monthly_sales(self):
        current_purchases_sum = Sale.objects.filter(sale_date__month=self.month, sale_date__year=self.year).count()
        current_income_sum = Sale.objects.filter(sale_date__month=self.month, sale_date__year=self.year).aggregate(total=Sum('total_price'))['total'] or 0
        previous_income_sum = Sale.objects.filter(sale_date__month=12 if self.month == 1 else self.previous_month,sale_date__year=self.previous_year).aggregate(total=Sum('total_price'))['total'] or 0
        income_diff = (
            ((current_income_sum - previous_income_sum) / ((current_income_sum + previous_income_sum) / 2)) * 100 
            if (current_income_sum + previous_income_sum) != 0 else 0
        )
        return current_income_sum, current_purchases_sum, income_diff

class ChartData:
    def __init__(self, month, year):
        self.month = month
        self.year = year

    def get_top_sales(self):
        sales_quantity_sum = Sale.objects.filter(sale_date__month=self.month, sale_date__year=self.year).values('product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:5]
        return {
            'labels': [item['product__name'] for item in sales_quantity_sum],
            'counts': [item['total_quantity'] for item in sales_quantity_sum],
        }

    def get_product_sales(self):
        sales_income_sum = Sale.objects.filter(sale_date__month=self.month, sale_date__year=self.year).values('product__name').annotate(total_price=Sum('total_price'))
        return {
            'labels': [item['product__name'] for item in sales_income_sum],
            'counts': [float(item['total_price']) for item in sales_income_sum],
        }

    def get_sales_by_month(self):
        sales_monthly_sum = Sale.objects.filter(sale_date__year=self.year).annotate(month=ExtractMonth('sale_date')).values('month').annotate(total_sales=Sum('total_price')).order_by('month')
        return {
            'labels': [calendar.month_name[item['month']] for item in sales_monthly_sum],
            'counts': [float(item['total_sales']) for item in sales_monthly_sum],
        }