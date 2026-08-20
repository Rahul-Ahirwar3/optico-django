from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.db import transaction
from django.contrib import messages
from django.db.models import Sum

import resend

from .models import (
    Contact,
    Customer,
    Product,
    Manufacturing,
    Issue,
    NetQuantity,
    Payment,
)


# ==================================================
# HOME PAGE
# ==================================================

def home(request):

    return render(
        request,
        'home.html'
    )


# ==================================================
# ABOUT PAGE
# ==================================================

def about(request):

    return render(
        request,
        'about.html'
    )


# ==================================================
# PRODUCTS PAGE
# ==================================================

def products(request):

    product_list = (
        Product.objects
        .all()
        .order_by('watt')
    )

    return render(
        request,
        'products.html',
        {
            'products': product_list
        }
    )


# ==================================================
# CONTACT PAGE
# ==================================================

def contact(request):

    if request.method == "POST":

        name = (
            request.POST.get('name', '')
            .strip()
        )

        email = (
            request.POST.get('email', '')
            .strip()
        )

        phone = (
            request.POST.get('phone', '')
            .strip()
        )

        message = (
            request.POST.get('message', '')
            .strip()
        )

        Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        try:

            resend.api_key = settings.RESEND_API_KEY

            resend.Emails.send({

                "from":
                    "Optico <onboarding@resend.dev>",

                "to": [
                    "ra362176@gmail.com"
                ],

                "subject":
                    "New Contact Form Submission - Optico",

                "html": f"""
                    <div style="
                        font-family: Arial, sans-serif;
                        max-width: 600px;
                        margin: auto;
                        padding: 25px;
                        border: 1px solid #ddd;
                        border-radius: 10px;
                    ">

                        <h2 style="color:#ff9800;">
                            New Contact Form Submission
                        </h2>

                        <hr>

                        <p>
                            <strong>Name:</strong> {name}
                        </p>

                        <p>
                            <strong>Email:</strong> {email}
                        </p>

                        <p>
                            <strong>Phone:</strong> {phone}
                        </p>

                        <p>
                            <strong>Message:</strong>
                        </p>

                        <div style="
                            background:#f5f5f5;
                            padding:15px;
                            border-radius:5px;
                        ">
                            {message}
                        </div>

                    </div>
                """
            })

        except Exception:

            pass

        return render(
            request,
            'contact.html',
            {
                'success':
                    'Message sent successfully! '
                    'Our team will contact you soon.'
            }
        )

    return render(
        request,
        'contact.html'
    )


# ==================================================
# LOGIN PAGE
# ==================================================

def login_view(request):

    if (
        request.user.is_authenticated
        and request.user.is_staff
    ):

        return redirect('/admin/')

    if request.method == "POST":

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if (
            user is not None
            and user.is_staff
        ):

            login(
                request,
                user
            )

            return redirect('/admin/')

        return render(
            request,
            'login.html',
            {
                'error':
                    'Invalid username or password.'
            }
        )

    return render(
        request,
        'login.html'
    )


# ==================================================
# ISSUE / SALE
# ==================================================

def issue_bulb(request):

    products = (
        Product.objects
        .all()
        .order_by('watt')
    )

    customers = (
        Customer.objects
        .all()
        .order_by('name')
    )

    total_stock = sum(
        product.available_stock
        for product in products
    )

    # ==================================================
    # POST
    # ==================================================

    if request.method == "POST":

        action = request.POST.get(
            'action'
        )

        # ==================================================
        # CREATE CUSTOMER
        # ==================================================

        if action == 'create_customer':

            new_customer_name = (
                request.POST.get(
                    'new_customer_name'
                ) or ''
            ).strip()

            if not new_customer_name:

                return render(
                    request,
                    'issue.html',
                    {
                        'products':
                            products,

                        'customers':
                            customers,

                        'total_stock':
                            total_stock,

                        'error':
                            'Please enter customer name.'
                    }
                )

            existing_customer = (
                Customer.objects
                .filter(
                    name__iexact=new_customer_name
                )
                .first()
            )

            if existing_customer:

                messages.info(
                    request,
                    f'Customer "{existing_customer.name}" '
                    f'already exists.'
                )

                return redirect(
                    'issue_bulb'
                )

            Customer.objects.create(
                name=new_customer_name
            )

            messages.success(
                request,
                f'Customer "{new_customer_name}" '
                f'created successfully.'
            )

            return redirect(
                'issue_bulb'
            )

        # ==================================================
        # ISSUE DATA
        # ==================================================

        product_id = request.POST.get(
            'product'
        )

        customer_id = request.POST.get(
            'customer'
        )

        quantity_value = request.POST.get(
            'quantity'
        )

        issue_date = request.POST.get(
            'issue_date'
        )

        rate_value = request.POST.get(
            'rate'
        )

        paid_value = request.POST.get(
            'paid_amount'
        )

        # ==================================================
        # PRODUCT
        # ==================================================

        if not product_id:

            return render(
                request,
                'issue.html',
                {
                    'products':
                        products,

                    'customers':
                        customers,

                    'total_stock':
                        total_stock,

                    'error':
                        'Please select a bulb.'
                }
            )

        try:

            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:

            return render(
                request,
                'issue.html',
                {
                    'products':
                        products,

                    'customers':
                        customers,

                    'total_stock':
                        total_stock,

                    'error':
                        'Product not found.'
                }
            )

        # ==================================================
        # CUSTOMER
        # ==================================================

        if not customer_id:

            return render(
                request,
                'issue.html',
                {
                    'products':
                        products,

                    'customers':
                        customers,

                    'total_stock':
                        total_stock,

                    'error':
                        'Please select a customer.'
                }
            )

        try:

            customer = Customer.objects.get(
                id=customer_id
            )

        except Customer.DoesNotExist:

            return render(
                request,
                'issue.html',
                {
                    'products':
                        products,

                    'customers':
                        customers,

                    'total_stock':
                        total_stock,

                    'error':
                        'Customer not found.'
                }
            )

        # ==================================================
        # QUANTITY
        # ==================================================

        try:

            quantity = int(
                quantity_value
            )

        except (
            TypeError,
            ValueError
        ):

            return render(
                request,
                'issue.html',
                {
                    'products':
                        products,

                    'customers':
                        customers,

                    'total_stock':
                        total_stock,

                    'error':
                        'Please enter a valid quantity.'
                }
            )

        if quantity <= 0:

            return render(
                request,
                'issue.html',
                {
                    'products':
                        products,

                    'customers':
                        customers,

                    'total_stock':
                        total_stock,

                    'error':
                        'Quantity must be greater than 0.'
                }
            )

        # ==================================================
        # RATE
        # ==================================================

        try:

            rate = Decimal(
                rate_value
            )

        except (
            TypeError,
            ValueError,
            InvalidOperation
        ):

            return render(
                request,
                'issue.html',
                {
                    'products':
                        products,

                    'customers':
                        customers,

                    'total_stock':
                        total_stock,

                    'error':
                        'Please enter a valid rate.'
                }
            )

        if rate < 0:

            return render(
                request,
                'issue.html',
                {
                    'products':
                        products,

                    'customers':
                        customers,

                    'total_stock':
                        total_stock,

                    'error':
                        'Rate cannot be negative.'
                }
            )

        # ==================================================
        # PAID AMOUNT
        # ==================================================

        try:

            paid_amount = Decimal(
                paid_value or 0
            )

        except (
            TypeError,
            ValueError,
            InvalidOperation
        ):

            return render(
                request,
                'issue.html',
                {
                    'products':
                        products,

                    'customers':
                        customers,

                    'total_stock':
                        total_stock,

                    'error':
                        'Please enter a valid payment.'
                }
            )

        if paid_amount < 0:

            return render(
                request,
                'issue.html',
                {
                    'products':
                        products,

                    'customers':
                        customers,

                    'total_stock':
                        total_stock,

                    'error':
                        'Paid amount cannot be negative.'
                }
            )

        # ==================================================
        # STOCK CHECK
        # ==================================================

        if quantity > product.available_stock:

            return render(
                request,
                'issue.html',
                {
                    'products':
                        products,

                    'customers':
                        customers,

                    'total_stock':
                        total_stock,

                    'error':
                        f'Not enough stock. '
                        f'Available stock: '
                        f'{product.available_stock}'
                }
            )

        # ==================================================
        # TOTAL AMOUNT
        # ==================================================

        total_amount = (
            Decimal(quantity) * rate
        )

        # ==================================================
        # PAID CHECK
        # ==================================================

        if paid_amount > total_amount:

            return render(
                request,
                'issue.html',
                {
                    'products':
                        products,

                    'customers':
                        customers,

                    'total_stock':
                        total_stock,

                    'error':
                        'Paid amount cannot be greater '
                        'than total amount.'
                }
            )

        # ==================================================
        # DUE
        # ==================================================

        due_amount = (
            total_amount - paid_amount
        )

        # ==================================================
        # SAVE ISSUE
        # ==================================================

        with transaction.atomic():

            Issue.objects.create(

                product=product,

                customer=customer,

                quantity=quantity,

                issue_date=issue_date,

                rate=rate,

                total_amount=total_amount,

                paid_amount=paid_amount,

                due_amount=due_amount

            )

        messages.success(
            request,
            'Bulb issued successfully.'
        )

        return redirect(
            'issue_bulb'
        )

    # ==================================================
    # PAGE
    # ==================================================

    return render(
        request,
        'issue.html',
        {
            'products':
                products,

            'customers':
                customers,

            'total_stock':
                total_stock,
        }
    )


# ==================================================
# INVENTORY PAGE
# ==================================================

def inventory(request):

    products = (
        Product.objects
        .all()
        .order_by('watt')
    )

    total_products = products.count()

    total_manufactured = sum(
        product.total_manufactured
        for product in products
    )

    total_available_stock = sum(
        product.available_stock
        for product in products
    )

    return render(
        request,
        'inventory.html',
        {
            'products':
                products,

            'total_products':
                total_products,

            'total_manufactured':
                total_manufactured,

            'total_available_stock':
                total_available_stock,
        }
    )


# ==================================================
# NET QUANTITY PAGE
# ==================================================

def net_quantity_view(request):

    products = (
        Product.objects
        .all()
        .order_by('watt')
    )

    total_products = products.count()

    total_manufactured = (
        Manufacturing.objects
        .aggregate(
            total=Sum(
                'quantity_manufactured'
            )
        )['total'] or 0
    )

    total_issue = (
        Issue.objects
        .aggregate(
            total=Sum(
                'quantity'
            )
        )['total'] or 0
    )

    net_quantity = max(
        total_manufactured - total_issue,
        0
    )

    product_data = []

    for product in products:

        manufactured = (
            Manufacturing.objects
            .filter(
                product=product
            )
            .aggregate(
                total=Sum(
                    'quantity_manufactured'
                )
            )['total'] or 0
        )

        issued = (
            Issue.objects
            .filter(
                product=product
            )
            .aggregate(
                total=Sum(
                    'quantity'
                )
            )['total'] or 0
        )

        product_net_quantity = max(
            manufactured - issued,
            0
        )

        net_record, created = (
            NetQuantity.objects.get_or_create(
                product=product
            )
        )

        if (
            net_record.total_manufactured
            != manufactured
            or
            net_record.total_issued
            != issued
            or
            net_record.net_quantity
            != product_net_quantity
        ):

            net_record.total_manufactured = (
                manufactured
            )

            net_record.total_issued = (
                issued
            )

            net_record.net_quantity = (
                product_net_quantity
            )

            net_record.save(
                update_fields=[
                    'total_manufactured',
                    'total_issued',
                    'net_quantity',
                    'updated_at',
                ]
            )

        product_data.append({

            'product':
                product,

            'manufactured':
                manufactured,

            'issued':
                issued,

            'net_quantity':
                product_net_quantity,

        })

    return render(
        request,
        'net_quantity.html',
        {
            'products':
                products,

            'total_products':
                total_products,

            'total_manufactured':
                total_manufactured,

            'total_issue':
                total_issue,

            'net_quantity':
                net_quantity,

            'product_data':
                product_data,
        }
    )


# ==================================================
# PRODUCT INVENTORY DETAIL
# ==================================================

def product_inventory(
    request,
    product_id
):

    try:

        product = Product.objects.get(
            id=product_id
        )

    except Product.DoesNotExist:

        return redirect(
            'inventory'
        )

    # ==================================================
    # POST - MANUFACTURING ENTRY
    # ==================================================

    if request.method == "POST":

        date = request.POST.get(
            'date'
        )

        workers = request.POST.get(
            'workers'
        )

        quantity = request.POST.get(
            'quantity_manufactured'
        )

        # ==================================================
        # DATE
        # ==================================================

        if not date:

            manufacturing_records = (
                Manufacturing.objects
                .filter(
                    product=product
                )
                .select_related('product')
                .order_by(
                    '-date',
                    '-id'
                )
            )

            return render(
                request,
                'product_inventory.html',
                {
                    'product':
                        product,

                    'manufacturing_records':
                        manufacturing_records,

                    'error':
                        'Please select a date.'
                }
            )

        # ==================================================
        # WORKERS
        # ==================================================

        try:

            workers = int(
                workers
            )

        except (
            TypeError,
            ValueError
        ):

            manufacturing_records = (
                Manufacturing.objects
                .filter(
                    product=product
                )
                .select_related('product')
                .order_by(
                    '-date',
                    '-id'
                )
            )

            return render(
                request,
                'product_inventory.html',
                {
                    'product':
                        product,

                    'manufacturing_records':
                        manufacturing_records,

                    'error':
                        'Number of workers must be a valid number.'
                }
            )

        if workers <= 0:

            manufacturing_records = (
                Manufacturing.objects
                .filter(
                    product=product
                )
                .select_related('product')
                .order_by(
                    '-date',
                    '-id'
                )
            )

            return render(
                request,
                'product_inventory.html',
                {
                    'product':
                        product,

                    'manufacturing_records':
                        manufacturing_records,

                    'error':
                        'Number of workers must be greater than 0.'
                }
            )

        # ==================================================
        # QUANTITY
        # ==================================================

        try:

            quantity = int(
                quantity
            )

        except (
            TypeError,
            ValueError
        ):

            manufacturing_records = (
                Manufacturing.objects
                .filter(
                    product=product
                )
                .select_related('product')
                .order_by(
                    '-date',
                    '-id'
                )
            )

            return render(
                request,
                'product_inventory.html',
                {
                    'product':
                        product,

                    'manufacturing_records':
                        manufacturing_records,

                    'error':
                        'Manufactured quantity must be a valid number.'
                }
            )

        if quantity <= 0:

            manufacturing_records = (
                Manufacturing.objects
                .filter(
                    product=product
                )
                .select_related('product')
                .order_by(
                    '-date',
                    '-id'
                )
            )

            return render(
                request,
                'product_inventory.html',
                {
                    'product':
                        product,

                    'manufacturing_records':
                        manufacturing_records,

                    'error':
                        'Manufactured quantity must be greater than 0.'
                }
            )

        # ==================================================
        # SAVE MANUFACTURING
        # ==================================================

        Manufacturing.objects.create(

            product=product,

            date=date,

            workers=workers,

            quantity_manufactured=quantity

        )

        messages.success(
            request,
            f'{quantity} products added successfully.'
        )

        return redirect(
            'product_inventory',
            product_id=product.id
        )

    # ==================================================
    # MANUFACTURING HISTORY
    # ==================================================

    manufacturing_records = (
        Manufacturing.objects
        .filter(
            product=product
        )
        .select_related('product')
        .order_by(
            '-date',
            '-id'
        )
    )

    return render(
        request,
        'product_inventory.html',
        {
            'product':
                product,

            'manufacturing_records':
                manufacturing_records,
        }
    )


# ==================================================
# MANUFACTURING HISTORY
# ==================================================

def manufacturing(request):

    manufacturing_records = (
        Manufacturing.objects
        .select_related('product')
        .order_by(
            '-date',
            '-id'
        )
    )

    total_manufactured = sum(
        item.quantity_manufactured
        for item in manufacturing_records
    )

    return render(
        request,
        'manufacturing.html',
        {
            'manufacturing_records':
                manufacturing_records,

            'total_manufactured':
                total_manufactured,
        }
    )


# ==================================================
# ISSUE HISTORY
# ==================================================

def issue_history(request):

    issues = (
        Issue.objects
        .select_related(
            'product',
            'customer'
        )
        .order_by(
            '-issue_date',
            '-id'
        )
    )

    total_issued = sum(
        issue.quantity
        for issue in issues
    )

    return render(
        request,
        'issue_history.html',
        {
            'issues':
                issues,

            'total_issued':
                total_issued,
        }
    )


# ==================================================
# DISTRIBUTOR DETAIL
# ==================================================

def distributor_detail(
    request,
    customer_id
):

    try:

        distributor = Customer.objects.get(
            id=customer_id
        )

    except Customer.DoesNotExist:

        return redirect(
            'issue_bulb'
        )

    # ==================================================
    # BULB FILTER
    # ==================================================

    bulb = request.GET.get(
        'bulb',
        ''
    )

    # ==================================================
    # ISSUES
    # ==================================================

    issues = (
        Issue.objects
        .filter(
            customer=distributor
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
    # OPTIONAL BULB FILTER
    # ==================================================

    if bulb:

        issues = issues.filter(
            product__watt=bulb
        )

    # ==================================================
    # TOTALS
    # ==================================================

    total_quantity = (
        issues.aggregate(
            total=Sum('quantity')
        )['total'] or 0
    )

    total_amount = (
        issues.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0')
    )

    paid_amount = (
        issues.aggregate(
            total=Sum('paid_amount')
        )['total'] or Decimal('0')
    )

    due_amount = (
        issues.aggregate(
            total=Sum('due_amount')
        )['total'] or Decimal('0')
    )

    return render(
        request,
        'distributor_detail.html',
        {
            'distributor':
                distributor,

            'issues':
                issues,

            'bulb':
                bulb,

            'total_quantity':
                total_quantity,

            'total_amount':
                total_amount,

            'paid_amount':
                paid_amount,

            'due_amount':
                due_amount,
        }
    )


# ==================================================
# ACCOUNT PAGE
# ==================================================

def account(request):

    # ==================================================
    # ALL DISTRIBUTORS / CUSTOMERS
    # ==================================================

    customers = (
        Customer.objects
        .all()
        .order_by('name')
    )

    # ==================================================
    # DEFAULT VALUES
    # ==================================================

    selected_customer = None

    issues = Issue.objects.none()

    bulbs = Product.objects.none()

    selected_customer_id = request.GET.get(
        'customer'
    )

    selected_bulb = request.GET.get(
        'bulb',
        ''
    ).strip()

    # ==================================================
    # SELECT CUSTOMER
    # ==================================================

    if selected_customer_id:

        try:

            selected_customer = (
                Customer.objects.get(
                    id=selected_customer_id
                )
            )

        except Customer.DoesNotExist:

            selected_customer = None

    # ==================================================
    # CUSTOMER ISSUE DATA
    # ==================================================

    if selected_customer:

        issues = (
            Issue.objects
            .filter(
                customer=selected_customer
            )
            .select_related(
                'product',
                'customer'
            )
            .order_by(
                '-issue_date',
                '-id'
            )
        )

        # ==================================================
        # BULB FILTER
        # ==================================================

        if selected_bulb:

            try:

                selected_bulb_id = int(
                    selected_bulb
                )

                issues = issues.filter(
                    product__id=selected_bulb_id
                )

            except (
                TypeError,
                ValueError
            ):

                pass

        # ==================================================
        # BULBS OF SELECTED CUSTOMER
        # ==================================================

        bulbs = (
            Product.objects
            .filter(
                issues__customer=selected_customer
            )
            .distinct()
            .order_by('watt')
        )

    # ==================================================
    # TOTAL AMOUNT
    # ==================================================

    total_amount = (
        issues.aggregate(
            total=Sum('total_amount')
        )['total']
        or Decimal('0')
    )

    # ==================================================
    # PAID AMOUNT
    # ==================================================

    paid_amount = (
        issues.aggregate(
            total=Sum('paid_amount')
        )['total']
        or Decimal('0')
    )

    # ==================================================
    # DUE AMOUNT
    # ==================================================

    due_amount = (
        issues.aggregate(
            total=Sum('due_amount')
        )['total']
        or Decimal('0')
    )

    # ==================================================
    # ACCOUNT PAGE
    # ==================================================

    return render(
        request,
        'account.html',
        {
            'customers':
                customers,

            'selected_customer':
                selected_customer,

            'issues':
                issues,

            'bulbs':
                bulbs,

            'selected_bulb':
                selected_bulb,

            'total_amount':
                total_amount,

            'paid_amount':
                paid_amount,

            'due_amount':
                due_amount,
        }
    )
# ==================================================
# ACCOUNT PAGE
# ==================================================

def account_view(request):

    customers = (
        Customer.objects
        .all()
        .order_by('name')
    )

    selected_customer_id = request.GET.get(
        'customer'
    )

    selected_product_id = request.GET.get(
        'bulb'
    )

    selected_customer = None
    selected_product = None
    issues = Issue.objects.none()

    total_amount = Decimal('0')
    paid_amount = Decimal('0')
    due_amount = Decimal('0')


    # ==================================================
    # CUSTOMER SELECTED
    # ==================================================

    if selected_customer_id:

        try:

            selected_customer = Customer.objects.get(
                id=selected_customer_id
            )

        except Customer.DoesNotExist:

            selected_customer = None


    # ==================================================
    # CUSTOMER + BULB DATA
    # ==================================================

    if selected_customer:

        issues = (
            Issue.objects
            .filter(
                customer=selected_customer
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
        # BULB SELECTED
        # ==================================================

        if selected_product_id:

            try:

                selected_product = Product.objects.get(
                    id=selected_product_id
                )

                issues = issues.filter(
                    product=selected_product
                )

            except Product.DoesNotExist:

                selected_product = None


        # ==================================================
        # TOTAL AMOUNT
        # ==================================================

        total_amount = (
            issues.aggregate(
                total=Sum(
                    'total_amount'
                )
            )['total']
            or Decimal('0')
        )


        # ==================================================
        # PAID AMOUNT
        # ==================================================

        paid_amount = (
            issues.aggregate(
                total=Sum(
                    'paid_amount'
                )
            )['total']
            or Decimal('0')
        )


        # ==================================================
        # DUE AMOUNT
        # ==================================================

        due_amount = (
            issues.aggregate(
                total=Sum(
                    'due_amount'
                )
            )['total']
            or Decimal('0')
        )


    # ==================================================
    # PRODUCTS FOR BULB DROPDOWN
    # ==================================================

    products = (
        Product.objects
        .all()
        .order_by('watt')
    )


    # ==================================================
    # RENDER
    # ==================================================

    return render(
        request,
        'account.html',
        {
            'customers':
                customers,

            'selected_customer':
                selected_customer,

            'selected_customer_id':
                selected_customer_id,

            'products':
                products,

            'selected_product':
                selected_product,

            'selected_product_id':
                selected_product_id,

            'issues':
                issues,

            'total_amount':
                total_amount,

            'paid_amount':
                paid_amount,

            'due_amount':
                due_amount,
        }
    )