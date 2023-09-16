from django.contrib import admin
from .models import Product,Variation
class ProductAdmin(admin.ModelAdmin):
    list_display=('product_name','price','stock','category')
    prepopulated_fields={'slug':('product_name',)}
class VartionAdmin(admin.ModelAdmin):
    list_display=('product','variation_category','variation_values','is_active') 
    list_editable=('is_active',)
    list_filter=('product','variation_category','variation_values') 

admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VartionAdmin)

# Register your models here.
