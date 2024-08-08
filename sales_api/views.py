import calendar

from django.shortcuts import render, get_object_or_404, redirect
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
    month = list(calendar.month_name)
    current_month = now().month
    month_name_to_number = {month: index for index, month in enumerate(calendar.month_name) if month}
    month_select = request.POST.get('months', calendar.month_name[current_month])
    month_select_val = month_name_to_number.get(month_select, current_month)

    current_year = now().year
    year_select = request.POST.get('year', current_year)

    previous_month = month_select_val - 1
    previous_year = year_select - 1 if month_select_val == 1 else year_select
    
    # Common filter
    sales_filter = {'sale_date__month': month_select_val, 'sale_date__year': year_select}
    
    monthly_purchases = Sale.objects.filter(**sales_filter).count()
    current_sales = Sale.objects.filter(**sales_filter).aggregate(total=Sum('total_price'))['total'] or 0
    previous_sales = Sale.objects.filter(
        sale_date__month=12 if month_select_val == 1 else previous_month,
        sale_date__year=previous_year
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # Calculate sales difference
    diff_sales = (
        ((current_sales - previous_sales) / ((current_sales + previous_sales) / 2)) * 100 
        if (current_sales + previous_sales) != 0 else 0
    )
    
    total_item = Product.objects.count()
    total_cust = Customer.objects.count()

    # Bar chart data
    top_sales = Sale.objects.filter(**sales_filter).values('product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
    bar_data = {
        'labels': [item['product__name'] for item in top_sales],
        'counts': [item['total_quantity'] for item in top_sales],
    }
    
    # Pie chart data
    product_sales = Sale.objects.filter(**sales_filter).values('product__name').annotate(total_price=Sum('total_price'))
    pie_data = {
        'labels': [item['product__name'] for item in product_sales],
        'counts': [float(item['total_price']) for item in product_sales],
    }

    # Line chart data for sales by month
    month_current_year = Sale.objects.filter(sale_date__year=year_select).annotate(month=ExtractMonth('sale_date')).values('month').annotate(total_sales=Sum('total_price')).order_by('month')
    line_data = {
        'labels': [calendar.month_name[item['month']] for item in month_current_year],
        'counts': [float(item['total_sales']) for item in month_current_year], 
    }

    context = {
        'month': month[1:],  # Exclude the empty string at index 0
        'month_name': month_select,
        'current_year': current_year,
        'year_select': year_select,
        
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

class DeleteMixin:
    model = None

    def post(self, request, *args, **kwargs):
        item_id = request.POST.get('itemId')
        item = get_object_or_404(self.model, id=item_id)
        item.delete()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return '/'  # Replace with the URL to redirect after deletion

# Table
class SalesSale(LoginRequiredMixin, DeleteMixin, ListView):
    model = Sale
    template_name = "sales_api/sales_sale.html"
    context_object_name = "sale_list"

    def get_success_url(self):
        return '/sales/sale/'

class SalesProduct(LoginRequiredMixin, DeleteMixin, ListView):
    model = Product
    template_name = "sales_api/sales_product.html"
    context_object_name = "products_list"

    def get_success_url(self):
        return '/sales/product/'

class SalesCustomer(LoginRequiredMixin, DeleteMixin, ListView):
    model = Customer
    template_name = "sales_api/sales_customer.html"
    context_object_name = "customers_list"

    def get_success_url(self):
        return '/sales/customer/'

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