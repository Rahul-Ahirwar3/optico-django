from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Contact,
    Customer,
    Product,
    Manufacturing,
    Inventory,
    Issue,
    NetQuantity,
    Payment,
    Account,
)


# ==================================================
# CONTACT
# ==================================================

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'email',
        'phone',
        'created_at',
    )

    search_fields = (
        'name',
        'email',
        'phone',
    )

    list_filter = (
        'created_at',
    )

    ordering = (
        '-created_at',
    )


# ==================================================
# CUSTOMER / DISTRIBUTOR
# ==================================================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'phone',
        'address',
        'created_at',
    )

    search_fields = (
        'name',
        'phone',
        'address',
    )

    ordering = (
        'name',
    )


# ==================================================
# MANUFACTURING INLINE
# ==================================================

class ManufacturingInline(admin.TabularInline):

    model = Manufacturing

    extra = 1

    fields = (
        'date',
        'workers',
        'quantity_manufactured',
        'total_stock',
    )

    readonly_fields = (
        'total_stock',
    )

    ordering = (
        '-date',
        '-id',
    )


# ==================================================
# ISSUE INLINE
# ==================================================

class IssueInline(admin.TabularInline):

    model = Issue

    extra = 0

    fields = (
        'customer',
        'quantity',
        'issue_date',
        'rate',
        'total_amount',
        'paid_amount',
        'due_amount',
    )

    readonly_fields = (
        'total_amount',
        'due_amount',
    )

    ordering = (
        '-issue_date',
        '-id',
    )


# ==================================================
# PRODUCT
# ==================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'watt',
        'total_manufactured',
        'available_stock',
        'price',
    )

    list_display_links = (
        'name',
    )

    search_fields = (
        'name',
        'description',
    )

    ordering = (
        'watt',
    )

    fieldsets = (

        (
            'Product Information',
            {
                'fields': (
                    'name',
                    'watt',
                    'description',
                    'image',
                    'price',
                )
            }
        ),

        (
            'Stock Information',
            {
                'fields': (
                    'total_manufactured',
                    'available_stock',
                )
            }
        ),

    )

    readonly_fields = (
        'total_manufactured',
        'available_stock',
    )

    inlines = [
        ManufacturingInline,
        IssueInline,
    ]


# ==================================================
# MANUFACTURING
# ==================================================

@admin.register(Manufacturing)
class ManufacturingAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'date',
        'workers',
        'quantity_manufactured',
        'total_stock',
        'created_at',
    )

    list_filter = (
        'date',
        'product',
    )

    search_fields = (
        'product__name',
    )

    ordering = (
        '-date',
        '-id',
    )

    readonly_fields = (
        'total_stock',
    )

    fieldsets = (

        (
            'Manufacturing Information',
            {
                'fields': (
                    'product',
                    'date',
                    'workers',
                    'quantity_manufactured',
                )
            }
        ),

        (
            'Stock Information',
            {
                'fields': (
                    'total_stock',
                )
            }
        ),

    )


# ==================================================
# INVENTORY
# ==================================================

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None
    ):
        return False

    def has_change_permission(
        self,
        request,
        obj=None
    ):
        return False

    def changelist_view(
        self,
        request,
        extra_context=None
    ):
        return redirect('/inventory/')


# ==================================================
# ISSUE / SALE
# ==================================================

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'customer',
        'quantity',
        'issue_date',
        'rate',
        'total_amount',
        'paid_amount',
        'due_amount',
    )

    search_fields = (
        'customer__name',
        'customer__phone',
        'product__name',
    )

    list_filter = (
        'issue_date',
        'product',
        'customer',
    )

    ordering = (
        '-issue_date',
        '-id',
    )

    readonly_fields = (
        'total_amount',
        'due_amount',
    )

    change_list_template = (
        'admin/website/issue/change_list.html'
    )

    fieldsets = (

        (
            'Sale / Issue Information',
            {
                'fields': (
                    'product',
                    'customer',
                    'quantity',
                    'issue_date',
                )
            }
        ),

        (
            'Payment Information',
            {
                'fields': (
                    'rate',
                    'total_amount',
                    'paid_amount',
                    'due_amount',
                )
            }
        ),

    )

    def get_queryset(self, request):

        queryset = super().get_queryset(request)

        distributor = request.GET.get('distributor')
        bulb = request.GET.get('bulb')

        if distributor:
            queryset = queryset.filter(
                customer_id=distributor
            )

        if bulb:
            queryset = queryset.filter(
                product__watt=bulb
            )

        return queryset

    def changelist_view(
        self,
        request,
        extra_context=None
    ):

        extra_context = extra_context or {}

        extra_context['distributors'] = (
            Customer.objects
            .all()
            .order_by('name')
        )

        extra_context['selected_distributor'] = (
            request.GET.get(
                'distributor',
                ''
            )
        )

        extra_context['selected_bulb'] = (
            request.GET.get(
                'bulb',
                ''
            )
        )

        return super().changelist_view(
            request,
            extra_context=extra_context
        )


# ==================================================
# NET QUANTITY
# ==================================================

@admin.register(NetQuantity)
class NetQuantityAdmin(admin.ModelAdmin):

    list_display = (
        'product',
        'total_manufactured',
        'total_issued_link',
        'net_quantity',
        'updated_at',
    )

    list_filter = (
        'product',
    )

    search_fields = (
        'product__name',
    )

    readonly_fields = (
        'product',
        'total_manufactured',
        'total_issued',
        'net_quantity',
        'updated_at',
    )

    ordering = (
        'product__watt',
    )

    fieldsets = (

        (
            'Net Quantity Information',
            {
                'fields': (
                    'product',
                    'total_manufactured',
                    'total_issued',
                    'net_quantity',
                    'updated_at',
                )
            }
        ),

    )

    @admin.display(
        description='Total Issued',
        ordering='total_issued'
    )
    def total_issued_link(self, obj):

        url = reverse(
            'admin:website_issue_changelist'
        )

        url += (
            f'?product__id__exact={obj.product.id}'
        )

        return format_html(
            '<a href="{}" '
            'style="font-weight:600;color:#0d6efd;">'
            '{}'
            '</a>',
            url,
            obj.total_issued
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(
        self,
        request,
        obj=None
    ):
        return False


# ==================================================
# PAYMENT
# ==================================================

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
        'issue__customer__name',
        'issue__product__name',
    )

    ordering = (
        '-payment_date',
        '-id',
    )

    fields = (
        'issue',
        'payment_date',
        'amount',
        'payment_method',
        'note',
    )


# ==================================================
# ACCOUNT
# ==================================================

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):

    list_display = (
        'customer_name',
        'total_amount_display',
        'paid_amount_display',
        'due_amount_display',
    )

    list_display_links = (
        'customer_name',
    )

    search_fields = (
        'customer__name',
        'customer__phone',
    )

    ordering = (
        'customer__name',
    )

    readonly_fields = (
        'customer',
        'total_amount_display',
        'paid_amount_display',
        'due_amount_display',
    )

    fields = (
        'customer',
        'total_amount_display',
        'paid_amount_display',
        'due_amount_display',
    )

    # ------------------------------------------
    # DISTRIBUTOR NAME
    # ------------------------------------------

    @admin.display(
        description='Distributor',
        ordering='customer__name'
    )
    def customer_name(self, obj):

        if obj.customer:
            return obj.customer.name

        return '-'

    # ------------------------------------------
    # TOTAL AMOUNT
    # ------------------------------------------

    @admin.display(
        description='Total Amount'
    )
    def total_amount_display(self, obj):

        return f"₹{obj.total_amount}"

    # ------------------------------------------
    # PAID AMOUNT
    # ------------------------------------------

    @admin.display(
        description='Paid Amount'
    )
    def paid_amount_display(self, obj):

        return f"₹{obj.paid_amount}"

    # ------------------------------------------
    # DUE AMOUNT
    # ------------------------------------------

    @admin.display(
        description='Due Amount'
    )
    def due_amount_display(self, obj):

        return f"₹{obj.due_amount}"

    # ------------------------------------------
    # ACCOUNT AUTOMATIC
    # ------------------------------------------

    def has_add_permission(self, request):

        return False

    # ------------------------------------------
    # DELETE DISABLE
    # ------------------------------------------

    def has_delete_permission(
        self,
        request,
        obj=None
    ):

        return False

    # ------------------------------------------
    # CHANGE DISABLE
    # ------------------------------------------

    def has_change_permission(
        self,
        request,
        obj=None
    ):

        return True