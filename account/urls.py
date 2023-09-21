from django.urls import path
from . import views
urlpatterns = [
    #path('',views.cart,name="cart"),
      path("register/",views.register,name="register"),
      path("login/",views.login,name="login"),
      path("logout/",views.logout,name="logout"),
      path('activate/<uidb64>/<token>/',views.activate,name="activate"),
      path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,name="resetpassword_validate"),
      path('dashboard/',views.dashboard,name="dashboard"),
      path('',views.dashboard,name="dashboard"),
      path('forgetPassword/',views.forgetPassword,name="forgetPassword"),
      path('restPassword/',views.restPassword,name="restPassword"),
      path('my_orders/',views.my_orders,name="my_orders"),
      path('edit_profile/',views.edit_profile,name="edit_profile"),
      path('changePassword/',views.changePassword,name="changePassword"),
      path('order_detail/<int:order_id>/',views.order_detail,name="order_detail")
    
   
   
]