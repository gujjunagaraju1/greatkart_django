from django.http import HttpResponse
from django.shortcuts import render
from store.models import Product,ReviewRating
def home(request):
    product=Product.objects.all().filter( is_available=True).order_by('created_date')
    for i in product:
        reviews=ReviewRating.objects.filter(product_id=i.id,status=True)
    context={
        'product':product,
        'reviews':reviews
    }
    return render(request,'home.html',context)