from django.contrib import admin
from .models import Product,Variation,ReviewRating,ProductGallery
import admin_thumbnails
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model=ProductGallery
    extra=1
    
class ProductAdmin(admin.ModelAdmin):
    list_display=('product_name','price','stock','category')
    prepopulated_fields={'slug':('product_name',)}
    inlines=[ProductGalleryInline]
class VartionAdmin(admin.ModelAdmin):
    list_display=('product','variation_category','variation_values','is_active') 
    list_editable=('is_active',)
    list_filter=('product','variation_category','variation_values') 

admin.site.register(Product,ProductAdmin)
admin.site.register(Variation,VartionAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGallery)

# Register your models here.
