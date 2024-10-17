from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, HTML
from django.contrib.auth.models import User
from .models import Customer, Product, Sale 

# User
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','password','first_name', 'last_name', 'email']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'data'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field ('username'),
            Field ('password', readonly='true'),
            Div (
                HTML ('Raw passwords are not stored, therefore unviewable. Click here if you want to <a class="is-colorized" href="{% url "password_change" %}">change password</a>'),
                css_class='is-size-7'
            ),
            HTML ('<hr>'),
            Div (
                Div (
                    Field('first_name'),
                ),
                Div (
                    Field('last_name'),
                    css_class='control is-expanded'
                ),
                css_class='field is-grouped'
            ),
            Field ('email'),
        )

# Sale
class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['customer','product','quantity','category']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'data'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div (
                Div (
                    Field('product'),
                ),
                Div (
                    Field('quantity'),
                    css_class='control is-expanded'
                ),
                css_class='field is-grouped'
            ),
            Field ('customer'),
            Field ('category'),
        )
        
# Products
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'data'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div (
                Div (
                    Field('name'),
                    css_class='control is-expanded'
                ),
                Div (
                    Field('price'),
                    css_class='control is-expanded'
                ),
                css_class='field is-grouped'
            ),
            Field('stock'),
        )
        
# Customer
class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = 'data'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div (
                Div (
                    Field('first_name'),
                    css_class='control is-expanded'
                ),
                Div (
                    Field('last_name'),
                    css_class='control is-expanded'
                ),
                css_class='field is-grouped'
            ),
            Field('email'),
            Field('phone_number'),
            Field('region_type'),
        )