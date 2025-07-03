from django.contrib import admin
from .models import *

@admin.register(TextCarouselMessage)
class TextCarouselMessageAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('text',)
    list_filter = ('is_active',)

admin.site.register(CarouselSlide)

@admin.register(ProductPerfume)
class ProductPerfumeAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'get_size_display', 'price', 'gender', 'scent_group', 'available',
        'is_featured', 'is_new', 'is_bestseller', 'is_scent_of_month', 'is_darkfem_collection', 'is_loveme_collection' 
    )
    list_editable = (
        'price', 'available', 'is_featured', 'is_new', 'is_bestseller', 'is_scent_of_month'
    )
    list_filter = (
        'available', 'gender', 'scent_group', 'size', 'is_featured', 'is_new',
        'is_bestseller', 'is_scent_of_month'
    )
    search_fields = ('name', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'price', 'picture', 'available')
        }),
        ('Product Details', {
            'fields': ('description', 'gender', 'scent_group', 'size')
        }),
        ('Scent Notes', {
            'fields': ('top_notes', 'middle_notes', 'base_notes'),
            'classes': ('collapse',),
        }),
        ('Display Options', {
            'fields': ('is_featured', 'is_new', 'is_bestseller', 'is_scent_of_month', 'is_darkfem_collection', 'is_loveme_collection') 
        }),
    )
    save_on_top = True

@admin.register(ProductListPhoto)
class ProductListPhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')

@admin.register(ScentOfMonthPhoto)
class ScentOfMonthPhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')

@admin.register(DarkfemCollectionPhoto)
class DarkfemCollectionPhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')

@admin.register(LovemeCollectionPhoto)
class LovemeCollectionPhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')

@admin.register(ProductCandle)
class ProductCandleAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'scent_group', 'available', 
                   'is_featured', 'is_new', 'is_bestseller')
    list_editable = ('price', 'available', 'is_featured', 'is_new', 'is_bestseller')
    list_filter = ('available', 'scent_group', 'is_featured', 'is_new', 'is_bestseller')
    search_fields = ('name', 'description')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'price', 'picture', 'available')
        }),
        ('Product Details', {
            'fields': ('description', 'scent_group')
        }),
        ('Scent Notes', {
            'fields': ('top_notes', 'middle_notes', 'base_notes'),
            'classes': ('collapse',),
        }),
        ('Display Options', {
            'fields': ('is_featured', 'is_new', 'is_bestseller')
        }),
    )
    save_on_top = True

