from django.contrib import admin
from .models import Contact, Product


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'email',
        'phone',
        'message',
        'created_at'
    )

    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'phone')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image')
    search_fields = ('name',)