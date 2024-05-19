from django.contrib import admin
from products.models import Cart, Market, Order


admin.site.register(Cart)
admin.site.register(Market)
admin.site.register(Order)