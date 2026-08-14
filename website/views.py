from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.conf import settings

from .models import Contact, Product


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

        # -------------------------
        # Save Contact in Database
        # -------------------------
        Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        # -------------------------
        # Send Confirmation Email
        # -------------------------
        send_mail(
            subject='Contact Form Submission Successful - Optico',

            message=f"""
Hello {name},

Thank you for contacting Optico.

Your message has been successfully received.

Our team will review your message and contact you soon.

--------------------------------
Your Submitted Details
--------------------------------

Name: {name}
Email: {email}
Phone: {phone}

Message:
{message}

--------------------------------

Thank you,
Optico Team
""",

            from_email=settings.DEFAULT_FROM_EMAIL,

            recipient_list=[email],

            fail_silently=False,
        )

        # -------------------------
        # Success Message
        # -------------------------
        return render(request, 'contact.html', {
            'success': 'Message sent successfully! A confirmation email has been sent to your email address.'
        })

    return render(request, 'contact.html')


# =========================
# Login Page
# =========================
def login_view(request):

    # Admin already logged in
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

            # Create login session
            login(request, user)

            # Open Django Admin
            return redirect('/admin/')

        else:

            return render(request, 'login.html', {
                'error': 'Invalid username or password.'
            })

    return render(request, 'login.html')