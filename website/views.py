from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.conf import settings

import resend

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

            # IMPORTANT:
            # Without custom domain, Resend testing
            # allows your own verified email only.
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

        # =========================
        # SUCCESS MESSAGE
        # =========================

        return render(request, 'contact.html', {
            'success':
            'Message sent successfully! Our team will contact you soon.'
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

            login(request, user)

            return redirect('/admin/')

        return render(request, 'login.html', {
            'error': 'Invalid username or password.'
        })

    return render(request, 'login.html')