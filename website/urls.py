from django.urls import path
from . import views


urlpatterns = [

    # ==================================================
    # WEBSITE
    # ==================================================

    path(
        '',
        views.home,
        name='home'
    ),

    path(
        'about/',
        views.about,
        name='about'
    ),

    path(
        'products/',
        views.products,
        name='products'
    ),

    path(
        'contact/',
        views.contact,
        name='contact'
    ),


    # ==================================================
    # LOGIN
    # ==================================================

    path(
        'login/',
        views.login_view,
        name='login'
    ),


    # ==================================================
    # ISSUE / SALE
    # ==================================================

    path(
        'issue/',
        views.issue_bulb,
        name='issue_bulb'
    ),


    # ==================================================
    # ISSUE HISTORY
    # ==================================================

    path(
        'issue-history/',
        views.issue_history,
        name='issue_history'
    ),


    # ==================================================
    # INVENTORY
    # ==================================================

    path(
        'inventory/',
        views.inventory,
        name='inventory'
    ),


    # ==================================================
    # NET QUANTITY
    # ==================================================

    path(
        'inventory/net-quantity/',
        views.net_quantity_view,
        name='net_quantity'
    ),


    # ==================================================
    # PRODUCT INVENTORY DETAIL
    # ==================================================

    path(
        'inventory/product/<int:product_id>/',
        views.product_inventory,
        name='product_inventory'
    ),


    # ==================================================
    # MANUFACTURING HISTORY
    # ==================================================

    path(
        'inventory/manufacturing/',
        views.manufacturing,
        name='manufacturing'
    ),


    # ==================================================
    # DISTRIBUTOR DETAIL
    # ==================================================

    path(
        'distributor/<int:customer_id>/',
        views.distributor_detail,
        name='distributor_detail'
    ),


    # ==================================================
    # ACCOUNT
    # ==================================================

    path(
        'account/',
        views.account,
        name='account'
    ),

]