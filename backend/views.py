from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, authenticate

from .models import MessageBox, Message

from rest_framework.decorators import api_view

from .serializers import (
    MessageBoxSerializer,
    MessageSerializerNoLimit,
    SendMessage,
    loginSerializer,
    GOIPWebhookSerializer,
)
from time import sleep

from django.shortcuts import redirect, render


@login_required
@api_view(["GET"])
def retrieveMessageBoxes1(request, goipPort):
    msgs = (
        MessageBox.objects.filter(user=request.user, goipPort=goipPort)
        .annotate(timestamp=Max("messages__timestamp"))
        .order_by("-timestamp")
        .exclude(messages__isnull=True)
    )
    msgs = MessageBoxSerializer(msgs, many=True, context={"numberMsgs": 1})
    return Response(msgs.data)


@login_required
@api_view(["GET"])
def updateRetrieveMessageBoxes1(request, goipPort, lastId):
    lastObj = Message.objects.get(id=lastId)

    msgs = (
        MessageBox.objects.filter(
            user=request.user,
            goipPort=goipPort,
            messages__timestamp__gt=lastObj.timestamp,
        )
        .annotate(timestamp=Max("messages__timestamp"))
        .order_by("-timestamp")
    )
    msgs = MessageBoxSerializer(msgs, many=True, context={"numberMsgs": 1})
    return Response(msgs.data)


@login_required
@api_view(["GET"])
def retrieveMessageBoxes(
    request, goipPort, requestId, requestType=None, lastMessage=None
):
    offsetReset = request.GET.get("offsetReset", False)
    requestId = str(requestId)

    if requestId not in request.session:
        request.session[requestId] = 0

    offset = request.session[requestId]

    msgs = (
        MessageBox.objects.filter(user=request.user, goipPort=goipPort)
        .annotate(timestamp=Max("messages__timestamp"))
        .order_by("-timestamp")
        .exclude(messages__isnull=True)
    )
    if requestType:
        lastObj = Message.objects.get(id=lastMessage)
        if requestType == 1:
            msgs = msgs[offset : offset + 10]
        elif requestType == 2:
            msgs = msgs.filter(messages__timestamp__gt=lastObj.timestamp)

    if requestType == None:
        msgs = msgs[:9]

    msgs = MessageBoxSerializer(msgs, many=True, context={"numberMsgs": 1})
    request.session[requestId] += len(msgs.data)
    print((request.session[requestId]))
    return Response(msgs.data)


@login_required
@api_view(["GET"])
def retrieveMessageBoxMessages(
    request, goipPort, messagebox, requestType=None, lastMessage=None
):
    msgs = Message.objects.filter(
        messageBox__id=messagebox,
        messageBox__goipPort=goipPort,
        messageBox__user=request.user,
    )
    if requestType:
        lastObj = Message.objects.get(id=lastMessage)
        if requestType == 1:
            msgs = msgs.filter(timestamp__lt=lastObj.timestamp)
        elif requestType == 2:
            msgs = msgs.filter(timestamp__gt=lastObj.timestamp)
    if requestType != 2:
        msgs = msgs[:10]
    msgs = MessageSerializerNoLimit(msgs, many=True)

    messagebox = MessageBox.objects.get(id=messagebox)
    messagebox.read = True
    messagebox.save()

    return Response(msgs.data)


@api_view(["POST"])
def sendMessage(request, goipPort):
    data = request.data
    data["port"] = goipPort

    if request.method == "POST":
        message = SendMessage(data=data, context={"request": request})
        if message.is_valid():
            message.save()

            return Response({"success": True, "errors": {}})

        return Response({"success": False, "errors": message.errors})


@api_view(["POST"])
def goipWebhook(request, serverId):
    data = request.data
    data["serverId"] = serverId

    if request.method == "POST":
        message = GOIPWebhookSerializer(data=data, context={"request": request})
        if message.is_valid():
            message.save()

            return Response({"success": True, "errors": {}})

        return Response({"success": False, "errors": message.errors})
