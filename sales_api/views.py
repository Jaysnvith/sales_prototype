import calendar

from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models.functions import ExtractMonth

from .models import Sale, Product, Customer
from .forms import UserForm, SaleForm, ProductForm, CustomerForm

def is_member(user):
    return user.groups.filter(name='Staff').exists()

# User
def profile_view(request):
    user = request.user

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('sales_api:user')
    else:
        form = UserForm(instance=user)

    return render(request, 'sales_api/sales_user.html', {'formuser': form})

# Dashboard
@login_required
def SalesDashboard(request):
    current_month = now().month
    previous_month = now().month - 1
    current_year = now().year
    previous_year = now().year - 1
    
    monthly_purchases = Sale.objects.filter(sale_date__month = current_month, sale_date__year = current_year).count()
    current_sales = Sale.objects.filter(sale_date__month = current_month, sale_date__year = current_year).aggregate(total = Sum('total_price'))['total']
    previous_sales = Sale.objects.filter(sale_date__month = 12 if current_month == 1 else previous_month, sale_date__year = previous_year if current_month == 1 else current_year).aggregate(total = Sum('total_price'))['total']
    diff_sales = ((current_sales - previous_sales) / ((current_sales + previous_sales) / 2)) * 100
    total_item = Product.objects.count()
    total_cust = Customer.objects.count()

    # Bar chart data
    top_sales = Sale.objects.filter(sale_date__month=current_month, sale_date__year=current_year).values('product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
    bar_data = {
        'labels': [item['product__name'] for item in top_sales],
        'counts': [item['total_quantity'] for item in top_sales],
    }
    
    # Pie chart data
    product_sales = Sale.objects.filter(sale_date__month=current_month, sale_date__year=current_year).values('product__name').annotate(total_price=Sum('total_price'))
    pie_data = {
        'labels': [item['product__name'] for item in product_sales],
        'counts': [float(item['total_price']) for item in product_sales],
    }

    month_current_year = Sale.objects.filter(sale_date__year=current_year).annotate(month=ExtractMonth('sale_date')).values('month').annotate(total_sales=Sum('total_price')).order_by('month')
    line_data = {
        'labels': [calendar.month_name[item['month']] for item in month_current_year],
        'counts': [float(item['total_sales']) for item in month_current_year], 
    }

    context = {
        'month_name': calendar.month_name[current_month],
        'current_year': current_year,
        
        'current_sales': current_sales,
        'diff_sales': diff_sales,
        'monthly_purchases': monthly_purchases,
        
        'total_item': total_item,
        'total_cust': total_cust,
        
        'bar_data': bar_data,
        'pie_data': pie_data,
        'line_data': line_data,
    }

    return render(request, 'sales_api/sales_dashboard.html', context)

# Report
def SalesReport(request):
    return render(request,'sales_api/sales_report.html')

# Table
class SalesSale(LoginRequiredMixin, ListView):
    model = Sale
    template_name = "sales_api/sales_sale.html"
    context_object_name = "sale_list"

class SalesProduct(LoginRequiredMixin, ListView):
    model = Product
    template_name = "sales_api/sales_product.html"
    context_object_name = "products_list"

class SalesCustomer(LoginRequiredMixin, ListView):
    model = Customer
    template_name = "sales_api/sales_customer.html"
    context_object_name = "customers_list"

# Create
class SaleCreate (LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name ="sales_api/sales_update.html"
    success_url = reverse_lazy("sales_api:sale")

class ProductCreate (LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name ="sales_api/sales_update.html"
    success_url = reverse_lazy("sales_api:product")  # Example reverse URL name

class CustomerCreate (LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name ="sales_api/sales_update.html"
    success_url = reverse_lazy("sales_api:customer")

# Update
class SaleUpdate (LoginRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleForm
    template_name ="sales_api/sales_update.html"
    success_url = reverse_lazy("sales_api:sale")

class ProductUpdate (LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name ="sales_api/sales_update.html"
    success_url = reverse_lazy("sales_api:product")

class CustomerUpdate (LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name ="sales_api/sales_update.html"
    success_url = reverse_lazy("sales_api:customer")
    
# Delete
class SaleDelete (LoginRequiredMixin, DeleteView):
    model = Sale
    template_name ="sales_api/sales_delete.html"
    success_url = reverse_lazy("sales_api:sale")

class ProductDelete (LoginRequiredMixin, DeleteView):
    model = Product
    template_name ="sales_api/sales_delete.html"
    success_url = reverse_lazy("sales_api:product")
    
class CustomerDelete (LoginRequiredMixin, DeleteView):
    model = Customer
    template_name ="sales_api/sales_delete.html"
    success_url = reverse_lazy("sales_api:customer")