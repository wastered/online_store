from django.contrib import admin
from parler.admin import TranslatableAdmin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    list_display = ['name', 'slug']

    fieldsets = (
        (None, {
            'fields': ('slug',)
        }),
        ('Translations', {
            'fields': ('name',),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(TranslatableAdmin):
    list_display = ['name', 'slug', 'price', 'category', 'available', 'created', 'updated']
    list_display_links = ['name', 'slug']
    list_filter = ['available', 'created', 'updated']
    list_editable = ['price', 'available']
    readonly_fields = ('created', 'updated')

    fieldsets = (
        (None, {
            'fields': ('slug', 'price', 'available', 'category', 'created', 'updated')
        }),
        ('Translations', {
            'fields': ('name', 'description'),
        }),
    )

    def get_prepopulated_fields(self, request, obj=None):
        return {'slug': ('name',)}
