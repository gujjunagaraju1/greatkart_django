from django.contrib import admin
from .models import Account
class AccountAdim(admin.ModelAdmin):
    list_display=['email','first_name','last_name','phone_number']
admin.site.register(Account,AccountAdim)

# Register your models here.
