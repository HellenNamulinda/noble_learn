from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'order_type', 'amount', 'status', 'created_at')
    list_filter = ('order_type', 'status')
    search_fields = ('user__email', 'course__title')
    readonly_fields = ('id', 'created_at', 'updated_at')
