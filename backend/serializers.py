
from rest_framework import serializers
from django.contrib import auth
from .models import *
from phonenumber_field.serializerfields import PhoneNumberField as PhoneNumber
from .utils import send_goip_sms
class LimitedListSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        data = data.all()[:1]
        return super(LimitedListSerializer, self).to_representation(data)

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['firstname','lastname','number']
        
class MessageSerializer(serializers.ModelSerializer):
    
    class Meta:
        list_serializer_class = LimitedListSerializer
        model = Message
        fields = ['id', 'messageType', 'message','timestamp']

class MessageBoxSerializer(serializers.ModelSerializer):

    messages = MessageSerializer(many=True, read_only=True)
    contact = ContentSerializer(source='contactInfo')
    class Meta:
        
        model = MessageBox
        fields = ['id', 'contact','messages','number']

class MessageSerializerNoLimit(serializers.ModelSerializer):
    
    class Meta:
        
        model = Message
        fields = ['id', 'messageType', 'message','timestamp']

class SendMessage(serializers.Serializer):


    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    port = serializers.UUIDField()
    number = serializers.CharField(max_length=200)
    message = serializers.CharField(max_length=200)


    def create(self,validated_data):
        user = validated_data['user']
        port = validated_data['port']
        goipPort = validated_data['goipPort']
        contact=validated_data['contact']

        msgBox, created = MessageBox.objects.get_or_create(user=user,goipPort=goipPort,number=validated_data['number'],contactInfo=contact)

        msg = Message.objects.create(messageBox=msgBox,message=validated_data['message'],messageType=0)

        goipPort_ = msgBox.goipPort
        sms_server = goipPort_.smsServer

        if sms_server:
            url = sms_server.url
            username = sms_server.username
            password = sms_server.password
            line = goipPort_.smsServerLine
            message = validated_data['message']
            phone_number = validated_data['number']
            final_phone_number = phone_number
            send_goip_sms(url,username,password,line,message,final_phone_number)
        return msg
    
    def validate(self,validated_data):
        user = validated_data['user']
        port = validated_data['port']
        try:
            validated_data['contact'] = Contact.objects.get(belongsTo=user,number=validated_data['number'])
        except Contact.DoesNotExist:
            validated_data['contact'] = None
        
        try:
            goipPort = GoIPPort.objects.get(user=user,id=port)
            validated_data['goipPort']=goipPort
        except GoIPPort.DoesNotExist:
            raise serializers.ValidationError('the user does NOT have access to the port')
        
        return validated_data

class GOIPWebhookSerializer(serializers.Serializer):

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    goip_line = serializers.CharField(max_length=200)
    from_number = serializers.CharField(max_length=200)
    content = serializers.CharField(max_length=1000)
    recv_time = serializers.DateTimeField()
    serverId = serializers.CharField(max_length=200)

    def create(self,validated_data):
        #get goip port, based on server and goip line
        server = validated_data['serverId']
        goip_line = validated_data['goip_line']
        user = validated_data['user']
        try:
            goipPort = GoIPPort.objects.get(smsServer=server,smsServerLine=goip_line)
            msgBox, created = MessageBox.objects.get_or_create(user=goipPort.user,goipPort=goipPort,number=validated_data['from_number'])
            msg = Message.objects.create(messageBox=msgBox,message=validated_data['content'],messageType=1)
            return msg
        except Exception as e:
            print(e)

class loginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=200)

    def login(self):
        validated_data = self.validated_data
        user = auth.authenticate(username=validated_data['email'], password=validated_data['password'])
        return user
