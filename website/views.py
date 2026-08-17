from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.db import transaction

import resend

from .models import Contact, Product, Issue, Payment


# =========================
# Home Page
# =========================
def home(request):
    return render(request, 'home.html')


# =========================
# About Page
# =========================
def about(request):
    return render(request, 'about.html')


# =========================
# Products Page
# =========================
def products(request):

    product_list = Product.objects.all()

    return render(request, 'products.html', {
        'products': product_list
    })


# =========================
# Contact Page
# =========================
def contact(request):

    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        # =========================
        # SAVE CONTACT DETAILS
        # =========================

        Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        # =========================
        # RESEND EMAIL
        # =========================

        resend.api_key = settings.RESEND_API_KEY

        resend.Emails.send({
            "from": "Optico <onboarding@resend.dev>",
            "to": ["ra362176@gmail.com"],
            "subject": "New Contact Form Submission - Optico",

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

                    <p>
                        Someone has submitted the contact
                        form on your Optico website.
                    </p>

                    <hr>

                    <h3>User Details</h3>

                    <p>
                        <strong>Name:</strong>
                        {name}
                    </p>

                    <p>
                        <strong>Email:</strong>
                        {email}
                    </p>

                    <p>
                        <strong>Phone:</strong>
                        {phone}
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

                    <hr>

                    <p>
                        This message was submitted
                        through the Optico website.
                    </p>

                </div>
            """
        })

        return render(request, 'contact.html', {
            'success':
            'Message sent successfully! Our team will contact you soon.'
        })

    return render(request, 'contact.html')


# =========================
# Login Page
# =========================
def login_view(request):

    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/')

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None and user.is_staff:

            login(request, user)

            return redirect('/admin/')

        return render(request, 'login.html', {
            'error': 'Invalid username or password.'
        })

    return render(request, 'login.html')


# ==================================================
# BULB ISSUE PAGE
# ==================================================

def issue_bulb(request):

    products = Product.objects.all().order_by('name')

    if request.method == "POST":

        product_id = request.POST.get('product')
        customer_name = request.POST.get('customer_name')
        quantity = request.POST.get('quantity')
        issue_date = request.POST.get('issue_date')
        rate = request.POST.get('rate')
        paid_amount = request.POST.get('paid_amount')

        # =========================
        # BASIC VALIDATION
        # =========================

        if not product_id:
            return render(request, 'issue.html', {
                'products': products,
                'error': 'Please select a bulb.'
            })

        if not customer_name:
            return render(request, 'issue.html', {
                'products': products,
                'error': 'Please enter customer name.'
            })

        try:
            quantity = int(quantity)
            rate = float(rate)
            paid_amount = float(paid_amount)

        except (TypeError, ValueError):

            return render(request, 'issue.html', {
                'products': products,
                'error': 'Please enter valid quantity, rate and payment.'
            })

        if quantity <= 0:

            return render(request, 'issue.html', {
                'products': products,
                'error': 'Quantity must be greater than 0.'
            })

        if rate < 0 or paid_amount < 0:

            return render(request, 'issue.html', {
                'products': products,
                'error': 'Rate and payment cannot be negative.'
            })

        # =========================
        # GET PRODUCT
        # =========================

        try:
            product = Product.objects.get(
                id=product_id
            )

        except Product.DoesNotExist:

            return render(request, 'issue.html', {
                'products': products,
                'error': 'Product not found.'
            })

        # =========================
        # CHECK STOCK
        # =========================

        if quantity > product.stock_quantity:

            return render(request, 'issue.html', {
                'products': products,
                'error': (
                    f'Not enough stock. '
                    f'Available stock: {product.stock_quantity}'
                )
            })

        # =========================
        # CHECK PAYMENT
        # =========================

        total_amount = quantity * rate

        if paid_amount > total_amount:

            return render(request, 'issue.html', {
                'products': products,
                'error': (
                    'Paid amount cannot be greater '
                    'than total amount.'
                )
            })

        # =========================
        # SAVE ISSUE + REDUCE STOCK
        # =========================

        with transaction.atomic():

            Issue.objects.create(
                product=product,
                customer_name=customer_name,
                quantity=quantity,
                issue_date=issue_date,
                rate=rate,
                total_amount=total_amount,
                paid_amount=paid_amount,
                due_amount=total_amount - paid_amount
            )

            # Reduce stock
            product.stock_quantity -= quantity
            product.save(
                update_fields=['stock_quantity']
            )

        # =========================
        # SUCCESS
        # =========================

        return redirect('issue_bulb')

    # =========================
    # AVAILABLE STOCK
    # =========================

    total_stock = sum(
        product.stock_quantity
        for product in products
    )

    return render(request, 'issue.html', {
        'products': products,
        'total_stock': total_stock
    })