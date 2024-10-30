import calendar

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView

from .models import Sale, Product, Customer
from .forms import UserForm, SaleForm, ProductForm, CustomerForm
from .services import DescAnalytic, ChartData, SalesReportGenerator

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
    months = list(calendar.month_name)[1:]  # Exclude the empty string at index 0
    current_month = now().month
    current_year = now().year

    # Mapping month name to its number
    month_name_to_number = {month: index for index, month in enumerate(months, start=1)}

    # Get selected month and year from POST data
    month_select = request.POST.get('months', calendar.month_name[current_month])
    month_select_val = month_name_to_number.get(month_select, current_month)
    year_select = int(request.POST.get('year', current_year))
    
    # Sales Order KPI
    desc_analytic = DescAnalytic(month_select_val, year_select)
    curr_revenue_total, curr_order_total, revenue_growth_rate, order_growth_rate = desc_analytic.monthly_totals()
    curr_aov, aov_growth_rate = desc_analytic.average_order()
    customer_total = desc_analytic.customer_insight()
    prod_order_monthly, prod_order_yearly, product_total, product_low = desc_analytic.product_insight()

    # Retrieve chart data
    chart_data = ChartData(month_select_val, year_select)
    annual_sales = chart_data.get_annual_sales()
    forecast_sales = chart_data.get_forecast_sales()
    prod_orders = chart_data.get_prod_orders()
    cust_orders = chart_data.get_cust_orders()
    stock_level = chart_data.get_product_stock()
    region_compare = chart_data.get_region_compare()
    
    if request.method == 'POST' and 'generate_pdf' in request.POST:
        report_generator = SalesReportGenerator(month_select, year_select, region_compare)
        response = report_generator.generate()
        return response   
    
    context = {
        # Date
        'date': {
            'month': months,
            'month_select': month_select,
            'current_year': current_year,
            'year_select': year_select,
        },

        # KPI
        'kpi': {
            'revenue': {
                'total': curr_revenue_total,
                'growth_rate': revenue_growth_rate,
            },
            'order': {
                'total': curr_order_total,
                'growth_rate': order_growth_rate,
            },
            'aov': {
                'total': curr_aov,
                'growth_rate': aov_growth_rate,
            },
            'products': {
                'monthly': prod_order_monthly,
                'yearly': prod_order_yearly,
                'total': product_total,
                'low': product_low,
            },
            'customers': {
                'total': customer_total,
            },
        },

        # Chart
        'charts': {
            'annual_sales': annual_sales,
            'forecast_sales': forecast_sales,
            'prod_orders': prod_orders,
            'cust_orders': cust_orders,
            'stock_level': stock_level,
            'region_compare': region_compare,
        },
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