from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect,  render
from django.urls import reverse
from backend.forms import signUpForm, loginForm
import stripe
from backend.models import UserInfo
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, JsonResponse,Http404
from backend.models import PlanPrice,UserCard,Subscription, GoIPPort
import uuid
import json


stripe.api_key="sk_test_51IqiplGO3c1oiuNYT3bPjZZzbJJUmfpPpP5cmiSRIHAtDmnHnmOkjUS0gJwMgYYaX9mjHFf1Aqr7a5xWvpvfYAhZ009FYiLuIb"

def index(request):
    plans = PlanPrice.objects.filter(isActive=True)
    monthlyPlans = plans.filter(paymentType='month')
    yearlyPlans = plans.filter(paymentType='year')
    return render(request, "index.html",context={'monthlyPlans':monthlyPlans,'yearlyPlans':yearlyPlans})

@login_required(redirect_field_name='next')
def checkout(request,planId):
    #getting the user
    user = request.user
    
    #checking if the plan that is being requested exist
    try:
        plan = PlanPrice.objects.get(id=planId)
    except:
        raise Http404("plan does not exist")

    if request.method == "GET":
        
        #creating stripe intent
        intent = stripe.SetupIntent.create(
            customer=user.info.stripeId,
            payment_method_types=["card"],
        )
        intentSecret = intent.get('client_secret')
        request.session['lastestIntentSecret']=intentSecret
        prices=[
            {
                'name':plan.name,
                'price':plan.price,
                'currency':plan.currency,
                'paymentType': plan.get_paymentType_display()
            },
            {
                'name':plan.activationPlanPrice.name,
                'price':plan.activationPlanPrice.price,
                'currency':plan.activationPlanPrice.currency,
                'paymentType': plan.activationPlanPrice.get_paymentType_display()
            }
        ]
        return render(
            request, 
            "shop-checkouts.html",
            context={
                'client_secret':intentSecret,
                'formData':plan.product.displayField.all().order_by('order'),
                'prices':prices,
                'productName':plan.product.name,
                'planId':planId
            }
        )

    if request.method == "POST":
        try:
            body_unicode = request.body.decode('utf-8')
            body = json.loads(body_unicode)
            if(body.get('stripeId')==request.session['lastestIntentSecret']):
                body['planId']=planId
                requestuuid = uuid.uuid4()
                request.session[str(requestuuid)]=body
                return JsonResponse({'status':1,'id':requestuuid})
        except:
            raise Http404("something went wrong")

@login_required()
def paymentSetup(request):

    user = request.user
    data = request.GET
    planData = request.session[data.get('confirmId')]
    intent = stripe.SetupIntent.retrieve(data.get('setup_intent'))
    idsMatch = (planData.get('stripeId')==intent.get('client_secret'))
    customeridsMatch = (user.info.stripeId==intent.get('customer'))
    successfull = (intent.get('status')== "succeeded")

    if(idsMatch and customeridsMatch and successfull):
        stripeCard = stripe.PaymentMethod.retrieve(intent.get('payment_method'))
        usercard = UserCard.objects.create(
            user=user,
            stripeId=stripeCard.get('id'),
            cardNumber=stripeCard['card']['last4'],
            expiryDate=f"{stripeCard['card']['exp_month']}/{stripeCard['card']['exp_year']}",
            nameOnCard=f"{stripeCard['billing_details']['name']}"
        )
        subscription = createSubscription(user,usercard,planData)
        if subscription:
            return redirect(reverse('frontend:dashboard'))
    raise Http404("Some thing is wrong contact support")

def createSubscription(user,userCard,planData):
    plan = PlanPrice.objects.get(id=planData.get('planId'))

    subscription = Subscription.objects.create(
        user = user,
        planPrice = plan,
        userCard = userCard,
        userData = planData,
        location=plan.get('simLocation')
    )
    return 1


@login_required(redirect_field_name='next')
def dashboard(request):
    user = request.user
    return render(request, "dashboard.html",context={'user':user,'navbarType':'dashboard'})


@login_required(redirect_field_name='next')
def sms(request,goipPort):
    user = request.user
    try:
        goip = GoIPPort.objects.get(id=goipPort)
    except:
        raise Http404("sms port does not exist")
    if(user == goip.user):
        return render(request, "sms.html",context={'user':user,'goipPort':goipPort,'uuid':uuid.uuid4()})
    raise Http404("You dont have access")


def loginView(request):

    redirectPage = request.GET.get('next','/')

    if request.user.is_authenticated:
        return redirect(redirectPage)

    if request.method == "GET":
        return render(request, 'registration/login.html',context={'next_url':redirectPage})

    if request.method == "POST":
        data = request.POST.copy()
        data['username'] = data['email']
        form = AuthenticationForm(None,data)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(redirectPage)
        return render(request, 'registration/login.html', context={'form': form,'next_url':redirectPage})

def signUpView(request):

    redirectPage = request.GET.get('next','/')

    if request.user.is_authenticated:
        return redirect(redirectPage)

    if request.method == "GET":
        return render(request, 'registration/signup.html',context={'next_url':redirectPage})

    if request.method == "POST":

        data = request.POST.copy()
        data['username'] = data['email']
        form = signUpForm(data)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(redirectPage)

        return render(request, 'registration/signup.html', context={'form': form,'next_url':redirectPage})

def logOutView(request):
    logout(request)
    return redirect(reverse('frontend:index'))
