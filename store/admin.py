from django.contrib import admin
from .models import *

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_customer', 'product', 'quantity', 'date_added')
    list_filter = ('order__customer', 'product')
    search_fields = ('order__customer__name', 'product__name')
    ordering = ('-date_added',)

    def get_customer(self, obj):
        return obj.order.customer if obj.order else None
    get_customer.admin_order_field = 'order__customer'  # Allows column order sorting
    get_customer.short_description = 'Customer'  # Column header

admin.site.register(OrderItems, OrderItemAdmin)
admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(ShippingAddress)