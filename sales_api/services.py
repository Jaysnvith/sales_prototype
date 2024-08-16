import calendar
from io import BytesIO

from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart

from .models import Sale

# Sales Report
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

# Chart Data
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
        sales_income_sum = Sale.objects.filter(sale_date__month=self.month, sale_date__year=self.year).values('product__name').annotate(total_price=Sum('total_price')).order_by('-total_price')
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