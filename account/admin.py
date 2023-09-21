from django.contrib import admin
from .models import Account,UserProfile
from django.utils.html import format_html
class AccountAdim(admin.ModelAdmin):
    list_display=['email','first_name','last_name','phone_number']
class Userpof(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src="{}" width="30" style="border-radius:50;">'.format(object.profile_picture.url))
    thumbnail.short_description ="profile picture"
    list_display=['thumbnail','user','city','state','country']
admin.site.register(Account,AccountAdim)
admin.site.register(UserProfile,Userpof)

# Register your models here.
