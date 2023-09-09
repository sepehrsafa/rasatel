from django.contrib import admin
from django.urls import path
from . import views
app_name = 'frontend'
urlpatterns = [
    path('', views.index,name='index'),
    path('dashboard',views.dashboard,name='dashboard' ),
    path('sms/<str:goipPort>',views.sms,name='sms' ),    
    path('login',views.loginView,name='login'),
    path('signup',views.signUpView,name='signup'),
    path('logout',views.logOutView,name='logout'),
    path('checkout/paymentcomplete',views.paymentSetup,name="paymentSetup"),
    path('checkout/<str:planId>',views.checkout,name='checkout'),
]

