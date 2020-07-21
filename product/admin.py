from django.contrib import admin
from .models import ProductCategory, Option, OptionGroup, Product, ProductMedia, ProductOption, ProductStockPrice

# Register your models here.
admin.site.register(ProductCategory)
admin.site.register(Option)
admin.site.register(OptionGroup)
admin.site.register(Product)

@admin.register(ProductMedia)
class ProductMediaAdmin(admin.ModelAdmin):
    list_display = ('product', 'id', 'default', 'media_file', )

# admin.site.register(ProductMedia)
admin.site.register(ProductOption)
admin.site.register(ProductStockPrice)