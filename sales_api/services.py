from io import BytesIO

import pandas as pd
import requests
from statsmodels.tsa.arima.model import ARIMA

from django.conf import settings
from django.db.models import Sum
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics import renderPDF

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

        # Change data value here
        self.sales_df = pd.DataFrame(list(Sale.objects.values('quantity', 'product__name', 'customer__first_name', 'total_price', 'sale_date')))
        self.prod_df = pd.DataFrame(list(Product.objects.values('name', 'stock')))
        self.cust_df = pd.DataFrame(list(Customer.objects.values('region_type')))

    def get_annual_sales(self):
        annual_sales = self.sales_df[self.sales_df['sale_date'].dt.year == self.year]
        annual_sales.set_index('sale_date', inplace=True)
        monthly_sales = annual_sales.resample('ME').sum()
        return {
            'labels': monthly_sales.index.strftime('%B').tolist(),
            'counts': monthly_sales['total_price'].astype(float).tolist(),
        }

    def get_forecast_sales(self):
        forecast_df = self.sales_df[self.sales_df['sale_date'].dt.year == self.year][['sale_date', 'total_price']]
        forecast_df.set_index('sale_date', inplace=True)
        forecast_df['total_price'] = pd.to_numeric(forecast_df['total_price'])
        monthly_data = forecast_df.resample('ME').sum()

        no_forecast = {'labels': [], 'counts': []}
        
        if monthly_data.empty:
            return no_forecast
        
        model = ARIMA(monthly_data['total_price'], order=(2, 1, 0))
        
        try:
            results = model.fit()
        except Exception as e:
            print(f"Error fitting ARIMA model: {e}")
            return no_forecast

        remainingMonth = int(12 - self.sales_df['sale_date'].dt.month.max())

        if remainingMonth <= 0:
            return no_forecast
        
        forecast = results.forecast(steps=remainingMonth)
        forecast.index = pd.to_datetime(forecast.index)

        return {
            'labels': [date.strftime('%B') for date in forecast.index],
            'counts': forecast.round().tolist(), 
            'summary': results.summary().as_html()
        }

    def get_prod_orders(self):
        products_df = self.sales_df[['sale_date', 'product__name', 'quantity']]
        
        annual_products = products_df[products_df['sale_date'].dt.year == self.year]
        annual_top_products = annual_products.groupby('product__name')['quantity'].sum().reset_index().sort_values(by='quantity', ascending=False)

        monthly_products = annual_products[annual_products['sale_date'].dt.month == self.month]
        monthly_top_products = monthly_products.groupby('product__name')['quantity'].sum().reset_index().sort_values(by='quantity', ascending=False)
        
        return {
            'monthly_labels': monthly_top_products['product__name'].tolist(),
            'monthly_counts': monthly_top_products['quantity'].tolist(),
            'yearly_labels': annual_top_products['product__name'].tolist(),
            'yearly_counts': annual_top_products['quantity'].tolist(),
        }

    def get_cust_orders(self):
        customer_df = self.sales_df[['sale_date', 'customer__first_name', 'quantity']]
        
        annual_customer = customer_df[customer_df['sale_date'].dt.year == self.year]
        annual_customer_group = annual_customer.groupby('customer__first_name')['quantity'].sum().reset_index().sort_values(by='quantity', ascending=False)

        monthly_customer = annual_customer[annual_customer['sale_date'].dt.month == self.month]
        monthly_customer_group = monthly_customer.groupby('customer__first_name')['quantity'].sum().reset_index().sort_values(by='quantity', ascending=False)
        
        return {
            'monthly_labels': monthly_customer_group['customer__first_name'].tolist(),
            'monthly_counts': monthly_customer_group['quantity'].tolist(),
            'yearly_labels': annual_customer_group['customer__first_name'].tolist(),
            'yearly_counts': annual_customer_group['quantity'].tolist(),
        }
    
    def get_product_stock(self):
        stock_df = self.prod_df[['name', 'stock']].sort_values(by='name')
        return {
            'labels': stock_df['name'].tolist(),
            'counts': stock_df['stock'].tolist(),
        }
    
    def get_region_compare(self):
        cust_region_df = self.cust_df[['region_type']].groupby('region_type').size().reset_index(name='count')
        return {
            'labels': cust_region_df['region_type'].tolist(),
            'counts': cust_region_df['count'].tolist(),
        }

#  openexchangerates API
def get_exchange_rates():
    url = "https://openexchangerates.org/api/latest.json"
    params = {
        "app_id": settings.EXCHANGE_API_KEY,  # Your API key
        "base": "USD",                        # Base currency (USD)
        "symbols": "IDR,JPY,USD"              # Only fetch IDR and JPY rates
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()       # Parse JSON response
        return data["rates"]         # Return the exchange rates
    except requests.RequestException as e:
        print("Error fetching exchange rates:", e)
        return None

# Generate PDF
class GenerateReport:
    def __init__(self, month: str, year: int, rev_total: float, order_total: int, aov: float, annual_sales: dict, prod_orders: dict, cust_orders: dict):
        self.title = "Laporan Sales"
        self.month = month
        self.year = year
        self.rev_total = rev_total
        self.order_total = order_total
        self.aov = aov
        self.annual_sales = [int(value) for value in annual_sales['counts']]
        self.prod_orders_counts = [int(value) for value in prod_orders['monthly_counts']]
        self.prod_orders_labels = prod_orders['monthly_labels']
        self.cust_orders_counts = [int(value) for value in cust_orders['monthly_counts']]
        self.cust_orders_labels = cust_orders['monthly_labels']

    def report_pdf(self) -> HttpResponse:
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)
        
        # Add header, chart, and summary
        self.add_header(p)
        self.add_line_chart(p, self.annual_sales, 100, 550)
        self.add_summary(p)
        self.add_bar_chart(p, self.prod_orders_counts, self.prod_orders_labels, 100, 250, "Sales by Products")
        self.add_bar_chart(p, self.cust_orders_counts, self.cust_orders_labels, 100, 50, "Sales by Customer")
        
        # Save PDF to buffer and return HTTP response
        p.showPage()
        p.save()
        buffer.seek(0)
        
        return HttpResponse(buffer, content_type="application/pdf", headers={"Content-Disposition": "inline; filename='report.pdf'"})
    
    def add_header(self, p: canvas.Canvas):
        """Adds title and header to the PDF"""
        p.setFont("Helvetica-Bold", 18)
        p.drawString(100, 750, f"{self.title} - {self.month} {self.year}")
        p.line(100, 740, 500, 740)

    def add_summary(self, p: canvas.Canvas):
        """Adds summary text for revenue, order total, and average order value"""
        p.setFont("Helvetica", 11)
        self.draw_text(p, 100, 530, f"Revenue Total = Rp{self.format_currency(self.rev_total)}")
        self.draw_text(p, 100, 515, f"Average Order Value = Rp{self.format_currency(self.aov)}")
        self.draw_text(p, 100, 500, f"Order Total = {self.order_total}")

    def add_line_chart(self, p: canvas.Canvas, chart_data: list, posx: int, posy: int):
        """Adds a line chart to the PDF with sales data"""
        drawing = Drawing(700, 200)
        line_chart = LinePlot()
        
        # Set chart position and dimensions
        line_chart.x, line_chart.y = 50, 30
        line_chart.height, line_chart.width = 100, 340

        # Prepare data for LinePlot
        y_data = [chart_data]
        x_data = [list(range(len(y))) for y in y_data]
        data = list(zip(*x_data, *y_data))
        line_chart.data = [data]

        # Add chart title
        title = Label()
        title.setOrigin(200, 150)
        title.setText(f"{self.year} Overtime Sales")
        title.fontName = "Helvetica-Bold"
        title.fontSize = 12
        drawing.add(title)

        drawing.add(line_chart)
        renderPDF.draw(drawing, p, posx, posy)

    def add_bar_chart(self, p: canvas.Canvas, chart_data: list, chart_label: list, posx: int, posy: int, chart_title: str):
        # Create a Drawing object as a container for the chart
        drawing = Drawing(400, 200)

        # Initialize the BarChart and configure it
        bar_chart = VerticalBarChart()
        bar_chart.x = 50
        bar_chart.y = 50
        bar_chart.height = 100
        bar_chart.width = 340

        # Example data: categories (x) and values (y)
        data = [chart_data]
        bar_chart.data = data

        # Configure x-axis and y-axis labels
        bar_chart.categoryAxis.categoryNames = chart_label  # x-axis categories

        # Add a title to the chart
        title = Label()
        title.setOrigin(200, 180)
        title.setText(chart_title)
        title.fontName = "Helvetica-Bold"
        title.fontSize = 12
        drawing.add(title)

        # Add the BarChart to the drawing
        drawing.add(bar_chart)

        # Render the drawing onto the PDF canvas at specific coordinates
        renderPDF.draw(drawing, p, posx, posy)  # Adjust position as needed

    @staticmethod
    def format_currency(value: float) -> str:
        """Formats a float as currency without decimal points"""
        return f"{value:,.0f}"

    @staticmethod
    def draw_text(p: canvas.Canvas, x: int, y: int, text: str):
        """Draws a string on the PDF at specified coordinates"""
        p.drawString(x, y, text)