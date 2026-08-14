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

        # -------------------------
        # Save Contact Details
        # -------------------------
        Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        # -------------------------
        # Send Email using Resend
        # -------------------------
        resend.api_key = settings.RESEND_API_KEY

        resend.Emails.send({
            "from": "Optico <onboarding@resend.dev>",
            "to": [email],
            "subject": "Contact Form Submission Successful - Optico",
            "html": f"""
                <div style="
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: auto;
                    padding: 25px;
                    border: 1px solid #ddd;
                    border-radius: 10px;
                ">

                    <h2 style="color: #ff9800;">
                        Hello {name},
                    </h2>

                    <p>
                        Thank you for contacting
                        <strong>Optico</strong>.
                    </p>

                    <p>
                        Your message has been successfully received.
                        Our team will review your message and contact
                        you soon.
                    </p>

                    <hr>

                    <h3>Your Submitted Details</h3>

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

                    <p>
                        {message}
                    </p>

                    <hr>

                    <p>
                        Thank you,<br>
                        <strong>Optico Team</strong>
                    </p>

                </div>
            """
        })

        # -------------------------
        # Success Message
        # -------------------------
        return render(request, 'contact.html', {
            'success':
            'Message sent successfully! A confirmation email has been sent to your email address.'
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

        else:

            return render(request, 'login.html', {
                'error': 'Invalid username or password.'
            })

    return render(request, 'login.html')