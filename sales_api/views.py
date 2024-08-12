import calendar

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView

from .models import Sale, Product, Customer
from .forms import UserForm, SaleForm, ProductForm, CustomerForm

from .services import SalesData, ChartData

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
    month = list(calendar.month_name)[1:]  # Exclude the empty string at index 0
    current_month = now().month
    month_name_to_number = {month: index for index, month in enumerate(calendar.month_name) if month}
    month_select = request.POST.get('months', calendar.month_name[current_month])
    month_select_val = month_name_to_number.get(month_select, current_month)
    current_year = now().year
    year_select = int(request.POST.get('year', current_year))
    
    sales_data = SalesData(month_select_val, year_select)
    current_income_sum, current_purchases_sum, income_diff = sales_data.get_monthly_sales()
    
    total_item = Product.objects.count()
    total_cust = Customer.objects.count()

    chart_data = ChartData(month_select_val,year_select)
    bar_data = chart_data.get_top_sales()
    pie_data = chart_data.get_product_sales()
    line_data = chart_data.get_sales_by_month()

    context = {
        'month': month,
        'month_name': month_select,
        'current_year': current_year,
        'year_select': year_select,
        'current_sales': current_income_sum,
        'diff_sales': income_diff,
        'monthly_purchases': current_purchases_sum,
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
class SaleCreate(LoginRequiredMixin, CreateView):
    model = Sale
    form_class = SaleForm
    template_name = "sales_api/sales_update.html"
    success_url = reverse_lazy("sales_api:sale")

class ProductCreate(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "sales_api/sales_update.html"
    success_url = reverse_lazy("sales_api:product")

class CustomerCreate(LoginRequiredMixin, CreateView):
    model = Customer
    form_class = CustomerForm
    template_name = "sales_api/sales_update.html"
    success_url = reverse_lazy("sales_api:customer")

# Update
class SaleUpdate(LoginRequiredMixin, UpdateView):
    model = Sale
    form_class = SaleForm
    template_name = "sales_api/sales_update.html"
    success_url = reverse_lazy("sales_api:sale")

class ProductUpdate(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "sales_api/sales_update.html"
    success_url = reverse_lazy("sales_api:product")

class CustomerUpdate(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    template_name = "sales_api/sales_update.html"
    success_url = reverse_lazy("sales_api:customer")
