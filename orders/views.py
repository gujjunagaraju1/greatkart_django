from django.shortcuts import render,redirect
from django.http import HttpResponse
from cart.models import CartItem,Cart
from .forms import OrderForm
from .models import Order
import datetime
def place_order(request,total=0,quantity=0):
    current_user=request.user
    print(current_user)
    cart_items=CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count<=0:
        return redirect('store')
    grand_total=0
    tax=0
    for cart_item in cart_items:
        total+=(cart_item.product.price*cart_item.quantity)
        quantity+=cart_item.quantity
    tax=(1.5*total)/100
    grandTotal=total+tax
    print(grandTotal)
    if request.method=='POST':
        form=OrderForm(request.POST)
        print("welcome nagaraju")
        if form.is_valid():
            
            
            data=Order()
            
            data.first_name=form.cleaned_data['first_name']
            data.last_name=form.cleaned_data['last_name']
            data.phone=form.cleaned_data['phone']
            data.email=form.cleaned_data['email']
            data.address_line_1=form.cleaned_data['address_line_1']
            data.address_line_2=form.cleaned_data['address_line_2']
            data.country=form.cleaned_data['country']
            data.state=form.cleaned_data['state']
            data.city=form.cleaned_data['city']
            data.order_note=form.cleaned_data['order_note'] 
            data.order_total=grand_total
            data.tax=tax
            data.ip=request.META.get('REMOTE_ADDR')
            data.save()
            #go to generate id we use[ordere ]
            yr=int(datetime.date.today().strftime('%Y'))
            dt=int(datetime.date.today().strftime('%m'))
            mt=int(datetime.date.today().strftime('%d'))
            d=datetime.date(yr,dt,mt)
            current_date=d.strftime('%Y%m%d')
            order_number=current_date+str(data.id)
            data.order_number=order_number
            data.save()
            return redirect('cart')
        
        
    else:
        return redirect('cart')
   
            
