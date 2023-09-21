from django.shortcuts import render,redirect,get_object_or_404
from .forms import RegisterationForm,UserProfileForm,UserForms
from .models import UserProfile
from django.http import HttpResponse
from .models import Account
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from cart.models import Cart,CartItem
from cart.views import _cart_id
#email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests
from orders.models import Order,OrderProduct



def register(request):
    if request.method=="POST":
       form=RegisterationForm(request.POST)
       if form.is_valid():
           first_name=form.cleaned_data['first_name']
           last_name=form.cleaned_data['last_name']
           email=form.cleaned_data['email']
           phone_number=form.cleaned_data['phone_number']
           password=form.cleaned_data['password']
           username=email.split("@")[0]
           
           user=Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password)
           user.phone_number=phone_number
           user.save()
           #create user profile
           profile=UserProfile()
           profile.user_id=user.id
           profile.profile_picture="default/default.jpg"
           profile.save()
      
           #user activation
           current_site=get_current_site(request) # for different because we are now localhost
           mail_subject="Please activate your account"
           message=render_to_string('accounts/account_verification_email.html',{
               'user':user,
               'domain':current_site,
               'uid':urlsafe_base64_encode(force_bytes(user.pk)),
               'token':default_token_generator.make_token(user),})
           to_email=email
           send_mail=EmailMessage(mail_subject,message,to=[to_email])
           send_mail.send()
           
           messages.success(request,'thank you for registeration .For further we send the link to your mail please check it once and activate it')
           return redirect('register')
    else:
        form=RegisterationForm()
    context={
        'form':form
    }
    
    return render(request,'accounts/register.html',context)

def login(request):
    if request.method=="POST":
        email=request.POST['email']
        password=request.POST['password']
        
        user=auth.authenticate(email=email,password=password)
        if user is not None:
            try:
                cart=Cart.objects.get(cart_id=_cart_id(request)) 
                is_cart_item_exist=CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exist:
                    cart_item=CartItem.objects.filter(cart=cart)
                    for item in cart_item:
                        item.user=user
                        item.save()
                
                
 
            except:
                pass
               
            auth.login(request,user)
           # messages.success(request,'you are logged in')
            url=request.META.get('HTTP_REFERER')
            try:
                query=requests.utils.urlparse(url).query
                print(query)
                #next=/cart/checkout/
                params=dict(x.split("=") for x in query.split('&'))
                if 'next' in params:
                    nextPage=params['next']
                    return redirect(nextPage)
               
            except:
                 return redirect('dashboard')
        else:
            messages.error(request,'invalid login credentials')
            return redirect('login')
    
   
    return render(request,'accounts/login.html')
@login_required(login_url="login")  #this is import is person not loginand try to logout it takes that person to login page
def logout(request):
    auth.logout(request)
    messages.success(request,"you are login out") 
    return redirect('login')

def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
        
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'congrats your account is activated')
        return redirect('login')
    else:
        messages.error(request,"link is expired")
        return redirect('register')
        
        
        
# Create your views here.
@login_required(login_url="login") 
def dashboard(request):
    orders=Order.objects.order_by('-created_at').filter(user_id=request.user.id,is_ordered=True)
    orders_count=orders.count()
    userprofile=UserProfile.objects.get(user_id=request.user.id)
    context={
        'orders_count':orders_count,
        'userprofile':userprofile
    }
    return render(request,'accounts/dashboard.html',context)


def forgetPassword(request):
    if request.method=="POST":
        email=request.POST['email']
        if Account.objects.filter(email=email).exists():
            user=Account.objects.get(email__exact=email)
            #reset password
            current_site=get_current_site(request) # for different because we are now localhost
            mail_subject="Reset your password"
            message=render_to_string('accounts/reset_password_email.html',{
               'user':user,
               'domain':current_site,
               'uid':urlsafe_base64_encode(force_bytes(user.pk)),
               'token':default_token_generator.make_token(user),})
            to_email=email
            send_mail=EmailMessage(mail_subject,message,to=[to_email])
            send_mail.send()
            messages.success(request,'password reset send to mail')
            return redirect('login')
       
            
        else:
            messages.error(request,'account doesnot exist')
            return redirect('register')
    return render(request,'accounts/forgetPassword.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,'please reset your password sent to mail')
        return redirect('restPassword')
    else:
        messages.error(request,'this link is experied')
        return redirect('login')
    return  HttpResponse('ok')
def restPassword(request):
    if request.method=="POST":
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password==confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'password reset successfull')
            return redirect('login')
        else:
            messages.error(request,"password don't match")
            return redirect('restPassword')
    else:
        return render(request,'accounts/restPassword.html')
@login_required(login_url='login')
def my_orders(request):
    order=Order.objects.filter(user=request.user,is_ordered=True).order_by('-created_at')
    context={
        'order':order,
    }
    return render(request,'accounts/my_orders.html',context)
@login_required(login_url='login')
def edit_profile(request):
    userprofile=get_object_or_404(UserProfile,user=request.user)
    if request.method=="POST":
        user_form=UserForms(request.POST,instance=request.user)
        profile_form=UserProfileForm(request.POST,request.FILES,instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,"you are profile has updated")
            return redirect('edit_profile')
    else:
        user_form=UserForms(instance=request.user)
        profile_form=UserProfileForm(instance=userprofile)
    context={
        'user_form':user_form,
        'profile_form':profile_form,
        'userprofile':userprofile
    }
        
    return render(request,'accounts/edit_profile.html',context)
@login_required(login_url='login')
def changePassword(request):
    if request.method =="POST":
        current_password=request.POST['current_password']
        new_password=request.POST['new_password']
        confirm_password=request.POST['confirm_password']
        user=Account.objects.get(username__exact=request.user.username)
        if new_password == confirm_password :
            sucess=user.check_password(current_password)
            if sucess:
                user.set_password(new_password)
                user.save()
                messages.success(request,'updated password sucessfull')
                return redirect('changePassword')
            else:
                messages.error(request,'please enter valid password')
                return redirect('changePassword')
        else:
            messages.error(request,'password does not match!')
            return redirect('changePassword')
    return render(request,'accounts/changePassword.html')
@login_required(login_url='login')
def order_detail(request,order_id):
    order_detail=OrderProduct.objects.filter(order__order_number=order_id)
    order=Order.objects.get(order_number=order_id)
    sub_total=0
    for i in order_detail:
        sub_total+=i.product_price*i.quantity
        
    context={
        'order_detail':order_detail,
        'order':order,
        'sub_total':sub_total
    }
    return render(request,'accounts/order_detail.html',context)
    
    