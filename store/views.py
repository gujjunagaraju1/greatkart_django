from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.http import HttpResponse
from .models import Product,ReviewRating,ProductGallery
from django.db.models import Q
from category.models import Category
from cart.models import Cart,CartItem
from cart.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from .forms import ReviewForm
from orders.models import Order,OrderProduct

def store(request,category_slug=None):
    categories=None
    products=None
    if category_slug !=None:
        categories=get_object_or_404(Category,slug=category_slug)
        product=Product.objects.filter(category=categories,is_available=True)
        paginator=Paginator(product,1)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=product.count()
    else:
        product=Product.objects.all().filter(is_available=True).order_by('id')
        paginator=Paginator(product,3)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count=product.count()
    context={
        'product':paged_products,
        'product_count':product_count,
        
    }
    
    return render(request,'store/store.html',context)
def product_detail(request,category_slug,product_slug):
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
        
        
    except Exception as e:
        raise e
    if request.user.is_authenticated:
        try:
          orderproduct=OrderProduct.objects.filter(user=request.user,product_id=single_product.id).exists()
        except OrderProduct.DoesNotExist:
          orderproduct=None
    else:
        orderproduct=None
    
    #get the reviews
    reviews=ReviewRating.objects.filter(product_id=single_product.id,status=True)
    #get product gallery
    product_gallery=ProductGallery.objects.filter(product_id=single_product.id)
    
    context={'single_product':single_product,'in_cart':in_cart,'orderproduct':orderproduct,'reviews':reviews,'product_gallery':product_gallery}   
    
        
    return render(request,'store/product_detail.html',context)
def search(request):
    if 'keyword' in request.GET:
        keyword=request.GET['keyword']
        if keyword:
            product=Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count=product.count()
    context={'product':product,
             'product_count':product_count}
    return render(request,'store/store.html',context)



# Create your views here.
def submit_review(request,product_id):
    url=request.META.get('HTTP_REFERER')
    if request.method=="POST":
        try:
            reviews=ReviewRating.objects.get(user__id=request.user.id,product__id=product_id)
            form=ReviewForm(request.POST,instance=reviews)
            form.save()
            messages.success(request,'thank you ! Your review has been updated')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form=ReviewForm(request.POST)
            if form.is_valid():
                data=ReviewRating()
                data.subject=form.cleaned_data['subject']
                data.rating=form.cleaned_data['rating']
                data.review=form.cleaned_data['review']
                data.ip=request.META.get('REMOTE_ADDR')
                data.product_id=product_id
                data.user_id=request.user.id
                data.save()
                messages.success(request,'your review submited')
                return redirect(url)
                
                
