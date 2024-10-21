import calendar
from io import BytesIO

from django.db.models import Sum, Count
from django.db.models.functions import ExtractMonth
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

from .models import Sale, Customer, Product

# Sales Report
class DescAnalytic:
    def __init__(self, month, year):
        self.month = month
        self.year = year
        self.previous_month = self.month - 1
        self.previous_year = self.year - 1 if month == 1 else self.year

    # Calculate total revenue and order count for a specific month and year
    def _get_totals(self, month, year):
        revenue_total = round(Sale.objects.filter(sale_date__month=month, sale_date__year=year).aggregate(total=Sum('total_price'))['total'] or 0)
        order_total = Sale.objects.filter(sale_date__month=month, sale_date__year=year).count()
        return revenue_total, order_total

    # Calculate growth rate
    def _get_growth_rate(self, current, previous):
        if (current + previous) == 0:
            return 0
        return ((current - previous) / ((current + previous) / 2)) * 100
    
    def monthly_totals(self):
        curr_revenue_total, curr_order_total = self._get_totals(self.month, self.year)
        prev_revenue_total, prev_order_total = self._get_totals(12 if self.month == 1 else self.previous_month, self.previous_year)

        revenue_growth_rate = self._get_growth_rate(curr_revenue_total, prev_revenue_total)
        order_growth_rate = self._get_growth_rate(curr_order_total, prev_order_total)

        return curr_revenue_total, curr_order_total, revenue_growth_rate, order_growth_rate
    
    def average_order(self):
        curr_revenue_total, curr_order_total = self._get_totals(self.month, self.year)
        prev_revenue_total, prev_order_total = self._get_totals(12 if self.month == 1 else self.previous_month, self.previous_year)
        
        curr_aov = round(curr_revenue_total / curr_order_total) if curr_order_total != 0 else 0
        prev_aov = round(prev_revenue_total / prev_order_total) if prev_order_total != 0 else 0
        
        aov_growth_rate = self._get_growth_rate(curr_aov, prev_aov)

        return curr_aov, aov_growth_rate
    
    def customer_insight(self):
        customer_total = Customer.objects.count()
        
        return customer_total
    
    def product_insight(self):
        prod_order_monthly = Sale.objects.filter(sale_date__month=self.month, sale_date__year=self.year).aggregate(total=Sum('quantity'))['total'] or 0
        prod_order_yearly = Sale.objects.filter(sale_date__year=self.year).aggregate(total=Sum('quantity'))['total'] or 0
        product_total = Product.objects.aggregate(total=Sum('stock'))['total'] or 0
        product_low = list(Product.objects.filter(stock__lt=20).values('name', 'stock'))
        
        return prod_order_monthly, prod_order_yearly, product_total, product_low

# Chart Data
class ChartData:
    def __init__(self, month, year):
        self.month = month
        self.year = year

    def get_annual_sales(self):
        sales_monthly_sum = Sale.objects.filter(sale_date__year=self.year).annotate(month=ExtractMonth('sale_date')).values('month').annotate(total_sales=Sum('total_price')).order_by('month')
        return {
            'labels': [calendar.month_name[item['month']] for item in sales_monthly_sum],
            'counts': [float(item['total_sales']) for item in sales_monthly_sum],
        }

    def get_prod_orders_monthly(self):
        sales_top_products = Sale.objects.filter(sale_date__month=self.month, sale_date__year=self.year).values('product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
        return {
            'labels': [item['product__name'] for item in sales_top_products],
            'counts': [item['total_quantity'] for item in sales_top_products],
        }
    
    def get_prod_orders_yearly(self):
        sales_top_products = Sale.objects.filter(sale_date__year=self.year).values('product__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
        return {
            'labels': [item['product__name'] for item in sales_top_products],
            'counts': [item['total_quantity'] for item in sales_top_products],
        }
    
    def get_product_stock(self):
        product_stock_level = Product.objects.all().values('name', 'stock').order_by('name')
        return {
            'labels': [item['name'] for item in product_stock_level],
            'counts': [float(item['stock']) for item in product_stock_level],
        }
    
    def get_cust_orders_monthly(self):
        sales_quantity_sum = Sale.objects.filter(sale_date__month=self.month, sale_date__year=self.year).values('customer__first_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
        return {
            'labels': [item['customer__first_name'] for item in sales_quantity_sum],
            'counts': [item['total_quantity'] for item in sales_quantity_sum],
        }
    
    def get_cust_orders_yearly(self):
        sales_quantity_sum = Sale.objects.filter(sale_date__year=self.year).values('customer__first_name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
        return {
            'labels': [item['customer__first_name'] for item in sales_quantity_sum],
            'counts': [item['total_quantity'] for item in sales_quantity_sum],
        }
    
    def get_region_compare(self):
        cust_region_compare = Customer.objects.values('region_type').annotate(count=Count('id'))
        return {
            'labels': [item['region_type'] for item in cust_region_compare],
            'counts': [item['count'] for item in cust_region_compare],
        }

# Generate PDF
class SalesReportGenerator:

    def __init__(self, month, year, pie_data):
        self.month = month
        self.year = year
        self.pie_data = pie_data
        self.buffer = BytesIO()
        self.response = HttpResponse(content_type='application/pdf')
        self.response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        self.doc = SimpleDocTemplate(self.buffer, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.elements = []

    def create_title(self):
        title = Paragraph(f"Sales Report ({self.month}, {self.year})", self.styles['Title'])
        self.elements.append(title)
        self.elements.append(Spacer(1, 12))

    def create_header(self, text, style='Heading2'):
        header = Paragraph(text, self.styles[style])
        self.elements.append(header)
        self.elements.append(Spacer(1, 12))

    def create_table(self):
        data = [["Items", "Sales"]] + [list(pair) for pair in zip(self.pie_data["labels"], self.pie_data["counts"])]
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        self.elements.append(table)
        self.elements.append(Spacer(1, 24))

    def create_bar_chart(self):
        drawing = Drawing(400, 200)
        bar_chart = VerticalBarChart()
        bar_chart.x = 50
        bar_chart.y = 50
        bar_chart.height = 125
        bar_chart.width = 300
        bar_chart.data = [[10000, 15000, 20000, 18000]]
        bar_chart.categoryAxis.categoryNames = ['January', 'February', 'March', 'April']
        bar_chart.bars[0].fillColor = colors.green
        bar_chart.valueAxis.valueMin = 0
        bar_chart.valueAxis.valueMax = 25000
        bar_chart.valueAxis.valueStep = 5000
        bar_chart.valueAxis.labelTextFormat = '$%d'
        drawing.add(bar_chart)
        self.elements.append(drawing)

    def build_pdf(self):
        self.create_title()
        self.create_header("Monthly Sales Data")
        self.create_table()
        self.create_header("Sales Overview")
        self.create_bar_chart()
        self.doc.build(self.elements)
        pdf = self.buffer.getvalue()
        self.buffer.close()
        self.response.write(pdf)
        return self.response

    def generate(self):
        return self.build_pdf()