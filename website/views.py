
# from django.shortcuts import render, redirect
# from .models import Contact


# # Home Page
# def home(request):
#     return render(request, 'home.html')


# # About Page
# def about(request):
#     return render(request, 'about.html')


# # Products Page
# def products(request):
#     return render(request, 'products.html')


# # Contact Page
# def contact(request):

#     if request.method == "POST":

#         name = request.POST.get('name')
#         email = request.POST.get('email')
#         phone = request.POST.get('phone')
#         message = request.POST.get('message')

#         Contact.objects.create(
#             name=name,
#             email=email,
#             phone=phone,
#             message=message
#         )

#         return redirect('contact')

#     return render(request, 'contact.html')


# # Login Page
# def login_view(request):
#     return render(request, 'login.html')


       
from django.shortcuts import render, redirect
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
    return render(request, 'login.html')