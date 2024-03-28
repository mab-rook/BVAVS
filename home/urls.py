from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('v_login', views.v_login, name='v_login'),
    path('vlogin', views.vlogin, name='vlogin'),
    path('v_register', views.v_register, name='v_register'),
    path('vregister', views.vregister, name='vregister'),
    path('admin_login', views.admin_login, name='admin_login'),
    path('adminlogin', views.adminlogin, name='adminlogin'),
    path('registervidpage', views.registervidpage, name='registervidpage'),
    path('forgotpassword', views.forgotpassword, name='forgotpassword'),
    path('forgot_password', views.forgot_password, name='forgot_password'),
    path('forgotpassotp', views.forgotpassotp, name='forgotpassotp'),
    path('setnewpassword', views.setnewpassword, name='setnewpassword'),
    path('logout', views.logout, name='logout'),
]