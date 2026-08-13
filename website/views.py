from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Contact, Product


# Home Page
def home(request):
    return render(request, 'home.html')


# About Page
def about(request):
    return render(request, 'about.html')


# Products Page
def products(request):
    product_list = Product.objects.all()

    return render(request, 'products.html', {
        'products': product_list
    })


# Contact Page
def contact(request):

    if request.method == "POST":

        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        return redirect('contact')

    return render(request, 'contact.html')


# Login Page
def login_view(request):

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