from django.urls import path
from . import views

app_name='sales_api'
urlpatterns = [
    path("user/", views.profile_view, name="user"),

    path("dashboard/", views.SalesDashboard, name="dashboard"),
    path("product/", views.SalesProduct.as_view(), name="product"),
    path("sale/", views.SalesSale.as_view(), name="sale"),
    path("customer/", views.SalesCustomer.as_view(), name="customer"),
    
    path("product/add/", views.ProductCreate.as_view(), name="productadd"),
    path("sale/add/", views.SaleCreate.as_view(), name="saleadd"),
    path("customer/add/", views.CustomerCreate.as_view(), name="customeradd"),

    path("product/item_<int:pk>/", views.ProductUpdate.as_view(), name="productedit"),
    path("sale/item_<int:pk>/", views.SaleUpdate.as_view(), name="saleedit"),
    path("customer/item_<int:pk>/", views.CustomerUpdate.as_view(), name="customeredit"),
    
    path("product/del_item_<int:pk>/", views.ProductDelete.as_view(), name="productdelete"),
    path("sale/del_item_<int:pk>/", views.SaleDelete.as_view(), name="saledelete"),
    path("customer/del_item_<int:pk>/", views.CustomerDelete.as_view(), name="customerdelete"),
]