from django.contrib import admin
from django.urls import path
from . import views
app_name='backend'
urlpatterns = [

    path('sms/retrieve/port/<uuid:goipPort>/messageboxes/<uuid:requestId>', views.retrieveMessageBoxes,name='retrieveMessageBoxes'),
    path('sms/update/retrieve/port/<uuid:goipPort>/messageboxes/<uuid:requestId>/<int:requestType>/<uuid:lastMessage>', views.retrieveMessageBoxes,name='updateRetrieveMessageBoxes'),
    path('sms/retrieve/port/<uuid:goipPort>/messagebox/<uuid:messagebox>/messages', views.retrieveMessageBoxMessages,name='retrieveMessageBoxMessagesNoLastId'),
    path('sms/retrieve/port/<uuid:goipPort>/messagebox/<uuid:messagebox>/messages/<int:requestType>/<uuid:lastMessage>', views.retrieveMessageBoxMessages,name='retrieveMessageBoxMessages'),
    path('sms/send/port/<uuid:goipPort>', views.sendMessage,name='sendMessage'),
    path('sms/webhook/server/<int:serverId>', views.goipWebhook,name='webhook'),
]


