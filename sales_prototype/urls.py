from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include("django.contrib.auth.urls")),
    path('accounts/', include("accounts.urls")),  
    path('sales/', include("sales_api.urls"))
]

admin.site.site_header = 'Sales Admin'
admin.site.site_url= '/sales/dashboard'