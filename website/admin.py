from django.contrib import admin
from .models import Contact, Product, Issue, Payment


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'email',
        'phone',
        'created_at',
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'stock_quantity',
        'price',
    )

    search_fields = ('name',)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'customer_name',
        'quantity',
        'issue_date',
        'rate',
        'total_amount',
        'paid_amount',
        'due_amount',
    )

    list_filter = (
        'issue_date',
        'product',
    )

    search_fields = (
        'customer_name',
        'product__name',
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'issue',
        'payment_date',
        'amount',
        'payment_method',
    )

    list_filter = (
        'payment_date',
        'payment_method',
    )

    search_fields = (
        'issue__customer_name',
    )