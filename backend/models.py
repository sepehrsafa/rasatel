from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.db import models
import uuid

#Models 

class UserInfo(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="info")
    stripeId = models.CharField(max_length=300)
    nationalId = models.CharField(max_length=20,blank=True)
    number = models.CharField(max_length=20,blank=True)

    def __str__(self):
        return f'{self.user} - stripeId: {self.stripeId}'

class UserCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="cards") 
    stripeId = models.CharField(max_length=200)
    cardNumber = models.CharField(max_length=20)
    expiryDate = models.CharField(max_length=7)
    nameOnCard = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.user} - stripeId: {self.stripeId}'

class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    firstname = models.CharField(max_length=200)
    lastname = models.CharField(max_length=200)
    number = models.CharField(max_length=20,blank=True)
    belongsTo = models.ForeignKey(User,on_delete=models.CASCADE,related_name='contacts')

    

    def __str__(self):
        return f'{self.firstname} {self.lastname}'

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=100)
    isActive = models.BooleanField(default=True)
    stripeId = models.CharField(max_length=200,blank=True)
    productModels = models.ManyToManyField(ContentType,blank=True,null=True)
    #features = ArrayField(models.CharField(max_length=100,blank=True,null=True),blank=True,null=True)
    def __str__(self):
        return f'{self.name} - stripeId: {self.stripeId}'

class PlanPrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)

    planTypes = [('onetime','یکبار'),('month','ماهانه'),('year','سالانه'),('week','هفتگی')]

    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="prices")
    activationPlanPrice = models.ForeignKey('self',on_delete=models.CASCADE,blank=True,null=True)
    currency = models.CharField(max_length=3,default='CAD')
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=6,decimal_places=2)
    paymentType = models.CharField(max_length=10,choices=planTypes)
    isActive = models.BooleanField(default=True)
    stripeId = models.CharField(max_length=200,blank=True)

    def __str__(self):
        return f'{self.product} - name: {self.name} - prince: {self.price}/{self.paymentType} stripeId: {self.stripeId}'

class Subscription(models.Model):
    carrierTypes = [(0,'آسیاتک'),(1,'همراه اول'),(2,'ایرانسل'),(3,'پیشگامان')]
    locationTypes = [(0,'ایران'),(1,'کانادا')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="subscriptions")
    planPrice = models.ForeignKey(PlanPrice,on_delete=models.CASCADE,related_name="subscriptions", blank=True,null=True)
    userCard = models.ForeignKey(UserCard,on_delete=models.CASCADE,related_name="subscriptions", blank=True,null=True)
    stripeId = models.CharField(max_length=200,blank=True)
    pricePlanSubscriptionStripeId= models.CharField(max_length=200,blank=True)
    isActive = models.BooleanField(default=False)
    currentPeriodEnd = models.DateTimeField(blank=True,null=True)
    goipPort = models.OneToOneField('GoIPPort',on_delete=models.CASCADE,related_name="subscription",blank=True,null=True)
    voip = models.OneToOneField('VoIP3CXAccount',on_delete=models.CASCADE,related_name="subscription",blank=True,null=True)
    carrier = models.IntegerField(choices=carrierTypes,blank=True,null=True)
    location = models.IntegerField(choices=locationTypes,blank=True,null=True)
    phonenumber = models.CharField(max_length=20,blank=True)
    userData = models.JSONField()


    def __str__(self):
        return f'{self.user} - plan: {self.planPrice} - userCard: {self.userCard}'

class Invoice(models.Model):
    paymentTypes = [(0,'کارت'),(1,'نقدی')]
    chargeTypes = [(0,'پرداخت'),(1,'بازگشت')]
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="invoices")
    paymentType = models.IntegerField(choices=paymentTypes)
    chargeType = models.IntegerField(choices=chargeTypes)
    amount = models.DecimalField(max_digits=10,decimal_places=2)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="invoices")
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

class VoIPServer(models.Model):
    name = models.CharField(max_length=255)
    numberSimCalls = models.IntegerField()
    location = models.CharField(max_length=255)
    ip = models.GenericIPAddressField(protocol="IPv4",unpack_ipv4=False)   

class GoIP(models.Model):
    goipTypes = [(0,'GSM goip'),(1,'Sim Banks')]
    name = models.CharField(max_length=255)
    numberOfPorts = models.IntegerField()
    location = models.CharField(max_length=255)
    goipType = models.IntegerField(choices=goipTypes)
    ip = models.GenericIPAddressField(protocol="IPv4",unpack_ipv4=False)

class SMSServer(models.Model):
    url = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)

class GoIPPort(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    goip = models.ForeignKey('GoIP',on_delete=models.CASCADE,related_name='messageBox')
    smsServer = models.ForeignKey('SMSServer',on_delete=models.CASCADE,related_name='messageBox',null=True,blank=True)
    smsServerLine = models.CharField(max_length=255,blank=True,null=True)
    simCardNumber = models.CharField(max_length=20,blank=True)

class MessageBox(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    goipPort = models.ForeignKey('GoIPPort',on_delete=models.CASCADE,related_name='messageBox')
    contactInfo = models.ForeignKey(Contact,on_delete=models.CASCADE,null=True,blank=True,related_name='messageBox')
    lastUpdate = models.DateTimeField(auto_now=True)
    number = models.CharField(max_length=20,blank=True)

    def __str__(self):
        return f'{self.number} box - {self.id} - lastUpdate: {self.lastUpdate}'
    
class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False,unique=True)
    messageTypes = [(0,'send'),(1,'receive')]
    messageBox = models.ForeignKey('MessageBox', on_delete=models.CASCADE,related_name="messages")
    messageType = models.IntegerField(choices=messageTypes)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    hasBeenRead = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'message number {self.messageBox}, text = {self.message}'

class VoIP3CXAccount(models.Model):
    
    server = models.ForeignKey(VoIPServer,on_delete=models.CASCADE,related_name='accounts')
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='voipAccounts')
    extention = models.IntegerField()

class DisplayField(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="displayField")
    inputType = models.CharField(max_length=100)
    inputId = models.CharField(max_length=100)
    inputName = models.CharField(max_length=100)
    inputPlaceholder =  models.CharField(max_length=100)
    options = models.ManyToManyField('DisplayFieldOptions',blank=True)
    order = models.IntegerField()
    required = models.BooleanField()

    class Meta:
        unique_together = ['product','order']
        verbose_name = 'DisplayField'
        verbose_name_plural = 'DisplayField'

class DisplayFieldOptions(models.Model):
    name = models.CharField(max_length=100)
    value=models.CharField(max_length=3)

