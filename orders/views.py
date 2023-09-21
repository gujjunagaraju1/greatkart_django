from django.shortcuts import render,redirect
from django.http import HttpResponse
from cart.models import CartItem,Cart
from .forms import OrderForm
from .models import Order,Payment,OrderProduct
import datetime
import json
from store.models import Product
#send invoice mail to user
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.mail import EmailMessage

def payments(request):
    body=json.loads(request.body)
    order=Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'])
    
    #store transcation details inside payment model
    payment=Payment(
        user=request.user,
        payment_id=body['transID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status']
    )
    payment.save()
    order.payment=payment
    order.is_ordered=True
    order.save()
    #move the cart items to order product table
    cart_items=CartItem.objects.filter(user=request.user)
    for item in cart_items :
        orderproduct=OrderProduct()
        orderproduct.order_id=order.id
        orderproduct.payment=payment
        orderproduct.user_id=request.user.id
        orderproduct.product_id=item.product_id
        orderproduct.quantity=item.quantity
        orderproduct.product_price=item.product.price
        orderproduct.ordered=True
        orderproduct.save()
        #reduce the quantity sold
        product=Product.objects.get(id=item.product_id)
        product.stock-=item.quantity
        product.save()
        
        
    
    
    
    
    #clear the cart
    CartItem.objects.filter(user=request.user).delete()
    
    #send order recived to customer
    user=request.user
    mail_subject="Thank you for your order please visit again"
    message=render_to_string('orders/order_received_email.html',{
               'user':user,
               'order':order,
               
              })
    to_email=request.user.email
    send_mail=EmailMessage(mail_subject,message,to=[to_email])
    send_mail.send()
    
    
    #send order transcation id back to senddata method using jasonresponse
    data={
        'order_number':order.order_number ,
        'transID':payment.payment_id,
        
        
    }
    
    
    
    return JsonResponse(data)
    
def place_order(request,total=0,quantity=0):
    current_user=request.user
    
    cart_items=CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count<=0:
        return redirect('store')
    total=0
    grand_total=0
    tax=0
    for cart_item in cart_items:
        total+=(cart_item.product.price*cart_item.quantity)
        quantity+=cart_item.quantity
    tax=(1.5*total)/100
    grand_total=total+tax
    
    if request.method=='POST':
        form=OrderForm(request.POST)
        
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
            data.user=request.user
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
            order=Order.objects.get(user=request.user,is_ordered=False,order_number=order_number)
            context={
                'order':order,
                'cart_items':cart_items,
                'tax':tax,
                'grand_total':grand_total,
                'total':total,
            }
           
            return render(request,'orders/payments.html',context)
        
        
    else:
        return redirect('cart')
    
def order_complete(request):
    order_number=request.GET.get('order_number')
    transID=request.GET.get('payment_id')
   
    try:
       
        order=Order.objects.get(order_number=order_number,is_ordered=True)
        
        
        order_product=OrderProduct.objects.filter(order_id=order.id)
        sub_total=0
        for i in order_product:
            sub_total+=i.product_price*i.quantity
        
        payment=Payment.objects.get(payment_id=transID)
        
        context={
            'order':order,
            'order_product':order_product,
            'order_number':order_number,
            'transID':payment.payment_id,
            'payment':payment,
            'sub_total':sub_total,
           
            
        }
        
        return render(request,'orders/order_complete.html',context)
    except (Payment.DoesNotExist,Order.DoesNotExist):
        return redirect('home')
   
   
            
