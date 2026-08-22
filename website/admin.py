from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html, format_html_join, mark_safe
from django.db.models import Sum, Q
from datetime import datetime

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
# CUSTOMER
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

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
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

    def has_delete_permission(self, request, obj=None):
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
        'total_quantity_display',
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
        'account_history',
    )

    fields = (
        'account_history',
    )

    # ==================================================
    # CHANGE VIEW
    # ==================================================

    def change_view(
        self,
        request,
        object_id,
        form_url='',
        extra_context=None
    ):

        self._account_request = request

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context
        )

    # ==================================================
    # CUSTOMER NAME
    # ==================================================

    @admin.display(
        description='Distributor',
        ordering='customer__name'
    )
    def customer_name(self, obj):

        if obj.customer:
            return obj.customer.name

        return '-'

    # ==================================================
    # TOTAL BULBS
    # ==================================================

    @admin.display(
        description='Total Bulbs'
    )
    def total_quantity_display(self, obj):

        return (
            Issue.objects
            .filter(
                customer=obj.customer
            )
            .aggregate(
                total=Sum('quantity')
            )['total'] or 0
        )

    # ==================================================
    # TOTAL AMOUNT
    # ==================================================

    @admin.display(
        description='Total Amount'
    )
    def total_amount_display(self, obj):

        return f"₹{obj.total_amount}"

    # ==================================================
    # PAID AMOUNT
    # ==================================================

    @admin.display(
        description='Paid Amount'
    )
    def paid_amount_display(self, obj):

        return f"₹{obj.paid_amount}"

    # ==================================================
    # DUE AMOUNT
    # ==================================================

    @admin.display(
        description='Due Amount'
    )
    def due_amount_display(self, obj):

        return f"₹{obj.due_amount}"

    # ==================================================
    # ACCOUNT HISTORY
    # ==================================================

    @admin.display(
        description=''
    )
    def account_history(self, obj):

        request = getattr(
            self,
            '_account_request',
            None
        )

        # ==================================================
        # SEARCH VALUE
        # ==================================================

        search = ''

        if request:

            search = (
                request.GET
                .get(
                    'history_search',
                    ''
                )
                .strip()
            )

        # ==================================================
        # PURCHASE HISTORY
        # ==================================================

        issues = (
            Issue.objects
            .filter(
                customer=obj.customer
            )
            .select_related(
                'product'
            )
            .order_by(
                '-issue_date',
                '-id'
            )
        )

        # ==================================================
        # SEARCH FILTER
        # ==================================================

        if search:

            search_query = Q()

            # PRODUCT NAME

            search_query |= Q(
                product__name__icontains=search
            )

            # WATT SEARCH
            # Supports:
            # 9
            # 9w
            # 9 W

            watt_search = (
                search
                .lower()
                .replace('w', '')
                .replace(' ', '')
                .strip()
            )

            if watt_search.isdigit():

                search_query |= Q(
                    product__watt=int(
                        watt_search
                    )
                )

            # DATE SEARCH

            searched_date = None

            date_formats = (
                '%d-%m-%Y',
                '%d/%m/%Y',
                '%Y-%m-%d',
            )

            for date_format in date_formats:

                try:

                    searched_date = (
                        datetime.strptime(
                            search,
                            date_format
                        ).date()
                    )

                    break

                except ValueError:
                    pass

            if searched_date:

                search_query |= Q(
                    issue_date=searched_date
                )

            issues = issues.filter(
                search_query
            )

        # ==================================================
        # PURCHASE HISTORY HTML
        # NO WATT COLUMN
        # ==================================================

        if issues.exists():

            purchase_html = format_html_join(
                '',
                '''
                <tr>

                    <td style="
                        padding:9px;
                        border:1px solid #ddd;
                        white-space:nowrap;
                    ">
                        {}
                    </td>

                    <td style="
                        padding:9px;
                        border:1px solid #ddd;
                    ">
                        {}
                    </td>

                    <td style="
                        padding:9px;
                        border:1px solid #ddd;
                        text-align:center;
                    ">
                        {}
                    </td>

                    <td style="
                        padding:9px;
                        border:1px solid #ddd;
                    ">
                        ₹{}
                    </td>

                    <td style="
                        padding:9px;
                        border:1px solid #ddd;
                    ">
                        ₹{}
                    </td>

                    <td style="
                        padding:9px;
                        border:1px solid #ddd;
                    ">
                        ₹{}
                    </td>

                    <td style="
                        padding:9px;
                        border:1px solid #ddd;
                    ">
                        ₹{}
                    </td>

                </tr>
                ''',

                (
                    (
                        issue.issue_date.strftime(
                            '%d-%m-%Y'
                        ),

                        issue.product.name,

                        issue.quantity,

                        issue.rate,

                        issue.total_amount,

                        issue.paid_amount,

                        issue.due_amount,
                    )

                    for issue in issues
                )
            )

        else:

            purchase_html = mark_safe(
                '''
                <tr>

                    <td
                        colspan="7"
                        style="
                            padding:20px;
                            text-align:center;
                            border:1px solid #ddd;
                            color:#777;
                        "
                    >
                        No purchase history found.
                    </td>

                </tr>
                '''
            )

        # ==================================================
        # PAYMENT HISTORY
        # WATT COLUMN REMOVED
        # ==================================================

        payments = (
            Payment.objects
            .filter(
                issue__customer=obj.customer
            )
            .select_related(
                'issue',
                'issue__product'
            )
            .order_by(
                '-payment_date',
                '-id'
            )
        )

        if payments.exists():

            payment_html = format_html_join(
                '',
                '''
                <tr>

                    <td style="
                        padding:9px;
                        border:1px solid #ddd;
                    ">
                        {}
                    </td>

                    <td style="
                        padding:9px;
                        border:1px solid #ddd;
                    ">
                        {}
                    </td>

                    <td style="
                        padding:9px;
                        border:1px solid #ddd;
                    ">
                        ₹{}
                    </td>

                    <td style="
                        padding:9px;
                        border:1px solid #ddd;
                    ">
                        {}
                    </td>

                    <td style="
                        padding:9px;
                        border:1px solid #ddd;
                    ">
                        {}
                    </td>

                </tr>
                ''',

                (
                    (
                        payment.payment_date.strftime(
                            '%d-%m-%Y'
                        ),

                        payment.issue.product.name,

                        payment.amount,

                        payment.payment_method,

                        payment.note or '-',
                    )

                    for payment in payments
                )
            )

        else:

            payment_html = mark_safe(
                '''
                <tr>

                    <td
                        colspan="5"
                        style="
                            padding:20px;
                            text-align:center;
                            border:1px solid #ddd;
                            color:#777;
                        "
                    >
                        No payment history found.
                    </td>

                </tr>
                '''
            )

        # ==================================================
        # ACCOUNT SUMMARY
        # ==================================================

        all_issues = (
            Issue.objects
            .filter(
                customer=obj.customer
            )
        )

        total_quantity = (
            all_issues
            .aggregate(
                total=Sum('quantity')
            )['total'] or 0
        )

        total_amount = (
            all_issues
            .aggregate(
                total=Sum('total_amount')
            )['total'] or 0
        )

        paid_amount = (
            all_issues
            .aggregate(
                total=Sum('paid_amount')
            )['total'] or 0
        )

        due_amount = (
            all_issues
            .aggregate(
                total=Sum('due_amount')
            )['total'] or 0
        )

        # ==================================================
        # SEARCH BAR
        # ==================================================

        search_bar = format_html(
            '''
            <div style="
                display:flex;
                align-items:center;
                gap:5px;
                margin:0;
            ">

                <input
                    id="account-history-search"
                    type="text"
                    value="{}"
                    placeholder="Date / Product..."
                    autocomplete="off"
                    style="
                        width:190px;
                        height:34px;
                        padding:5px 9px;
                        border:1px solid #aaa;
                        border-radius:4px;
                        font-size:13px;
                        box-sizing:border-box;
                    "
                >

                <button
                    type="button"
                    id="account-history-search-btn"
                    style="
                        height:34px;
                        padding:0 12px;
                        border:0;
                        border-radius:4px;
                        background:#417690;
                        color:white;
                        font-size:13px;
                        cursor:pointer;
                    "
                >
                    Search
                </button>

                <button
                    type="button"
                    id="account-history-clear-btn"
                    style="
                        height:34px;
                        padding:0 11px;
                        border:0;
                        border-radius:4px;
                        background:#777;
                        color:white;
                        font-size:13px;
                        cursor:pointer;
                    "
                >
                    Clear
                </button>

            </div>

            <script>
                (function() {{

                    function initAccountHistorySearch() {{

                        const input =
                            document.getElementById(
                                'account-history-search'
                            );

                        const searchButton =
                            document.getElementById(
                                'account-history-search-btn'
                            );

                        const clearButton =
                            document.getElementById(
                                'account-history-clear-btn'
                            );

                        if (
                            !input ||
                            !searchButton ||
                            !clearButton
                        ) {{
                            return;
                        }}

                        searchButton.onclick = function(e) {{

                            e.preventDefault();
                            e.stopPropagation();

                            const value =
                                input.value.trim();

                            const url =
                                new URL(
                                    window.location.href
                                );

                            if (value) {{

                                url.searchParams.set(
                                    'history_search',
                                    value
                                );

                            }} else {{

                                url.searchParams.delete(
                                    'history_search'
                                );

                            }}

                            window.location.href =
                                url.pathname +
                                (
                                    url.searchParams.toString()
                                        ? '?' +
                                          url.searchParams.toString()
                                        : ''
                                );
                        }};

                        input.onkeydown = function(e) {{

                            if (e.key === 'Enter') {{

                                e.preventDefault();
                                e.stopPropagation();

                                searchButton.click();
                            }}
                        }};

                        clearButton.onclick = function(e) {{

                            e.preventDefault();
                            e.stopPropagation();

                            const url =
                                new URL(
                                    window.location.href
                                );

                            url.searchParams.delete(
                                'history_search'
                            );

                            window.location.href =
                                url.pathname +
                                (
                                    url.searchParams.toString()
                                        ? '?' +
                                          url.searchParams.toString()
                                        : ''
                                );
                        }};

                    }}

                    if (
                        document.readyState === 'loading'
                    ) {{

                        document.addEventListener(
                            'DOMContentLoaded',
                            initAccountHistorySearch
                        );

                    }} else {{

                        initAccountHistorySearch();

                    }}

                }})();
            </script>
            ''',
            search,
        )

        # ==================================================
        # SEARCH STATUS
        # ==================================================

        if search:

            search_status = format_html(
                '''
                <div style="
                    margin:0 0 12px 0;
                    color:#666;
                    font-size:13px;
                ">
                    Showing results for:
                    <strong>{}</strong>
                </div>
                ''',
                search
            )

        else:

            search_status = ''

        # ==================================================
        # FINAL HTML
        # ==================================================

        return format_html(
            '''
            <div style="
                width:100%;
                margin:0;
                padding:0;
            ">

                <!-- SUMMARY -->

                <div style="
                    display:flex;
                    gap:10px;
                    flex-wrap:wrap;
                    margin-bottom:25px;
                ">

                    <div style="
                        background:#e8f4ff;
                        border:1px solid #b8dfff;
                        border-radius:5px;
                        padding:11px 16px;
                        min-width:135px;
                    ">

                        <div style="
                            font-size:12px;
                            color:#666;
                        ">
                            Total Bulbs
                        </div>

                        <div style="
                            font-size:20px;
                            font-weight:bold;
                        ">
                            {}
                        </div>

                    </div>

                    <div style="
                        background:#f5f5f5;
                        border:1px solid #ddd;
                        border-radius:5px;
                        padding:11px 16px;
                        min-width:135px;
                    ">

                        <div style="
                            font-size:12px;
                            color:#666;
                        ">
                            Total Amount
                        </div>

                        <div style="
                            font-size:20px;
                            font-weight:bold;
                        ">
                            ₹{}
                        </div>

                    </div>

                    <div style="
                        background:#eaf8ea;
                        border:1px solid #c5e6c5;
                        border-radius:5px;
                        padding:11px 16px;
                        min-width:135px;
                    ">

                        <div style="
                            font-size:12px;
                            color:#666;
                        ">
                            Paid Amount
                        </div>

                        <div style="
                            font-size:20px;
                            font-weight:bold;
                        ">
                            ₹{}
                        </div>

                    </div>

                    <div style="
                        background:#fff4e5;
                        border:1px solid #ffd9a3;
                        border-radius:5px;
                        padding:11px 16px;
                        min-width:135px;
                    ">

                        <div style="
                            font-size:12px;
                            color:#666;
                        ">
                            Due Amount
                        </div>

                        <div style="
                            font-size:20px;
                            font-weight:bold;
                        ">
                            ₹{}
                        </div>

                    </div>

                </div>


                <!-- PURCHASE HISTORY HEADER -->

                <div style="
                    display:flex;
                    align-items:center;
                    justify-content:space-between;
                    gap:12px;
                    margin-bottom:12px;
                ">

                    <h2 style="
                        margin:0;
                        font-size:20px;
                        font-weight:normal;
                    ">
                        Purchase History
                    </h2>

                    {}

                </div>


                {}


                <!-- PURCHASE HISTORY -->

                <div style="
                    overflow-x:auto;
                    margin-bottom:30px;
                ">

                    <table style="
                        width:100%;
                        min-width:750px;
                        border-collapse:collapse;
                        background:white;
                    ">

                        <thead>

                            <tr style="
                                background:#79aec8;
                                color:white;
                            ">

                                <th style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    Date
                                </th>

                                <th style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    Product
                                </th>

                                <th style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    Quantity
                                </th>

                                <th style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    Rate
                                </th>

                                <th style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    Total
                                </th>

                                <th style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    Paid
                                </th>

                                <th style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    Due
                                </th>

                            </tr>

                        </thead>

                        <tbody>
                            {}
                        </tbody>

                    </table>

                </div>


                <!-- PAYMENT HISTORY -->

                <h2 style="
                    background:#417690;
                    color:white;
                    padding:10px 13px;
                    margin:0 0 12px 0;
                    font-size:18px;
                    font-weight:normal;
                    border-radius:4px;
                ">
                    Payment History
                </h2>


                <div style="
                    overflow-x:auto;
                ">

                    <table style="
                        width:100%;
                        min-width:600px;
                        border-collapse:collapse;
                        background:white;
                    ">

                        <thead>

                            <tr style="
                                background:#79aec8;
                                color:white;
                            ">

                                <th style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    Payment Date
                                </th>

                                <th style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    Product
                                </th>

                                <th style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    Amount
                                </th>

                                <th style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    Method
                                </th>

                                <th style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    Note
                                </th>

                            </tr>

                        </thead>

                        <tbody>
                            {}
                        </tbody>

                    </table>

                </div>

            </div>
            ''',

            total_quantity,
            total_amount,
            paid_amount,
            due_amount,

            search_bar,
            search_status,

            purchase_html,

            payment_html,
        )

    # ==================================================
    # ADD DISABLED
    # ==================================================

    def has_add_permission(self, request):
        return False

    # ==================================================
    # DELETE DISABLED
    # ==================================================

    def has_delete_permission(
        self,
        request,
        obj=None
    ):
        return False

    # ==================================================
    # CHANGE ENABLED
    # ==================================================

    def has_change_permission(
        self,
        request,
        obj=None
    ):
        return True