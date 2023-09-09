from django.db.models.signals import post_save, pre_delete
from django.contrib.auth.models import User
from django.dispatch import receiver
import stripe
from .models import UserInfo, Product,PlanPrice,Subscription
import math
import datetime
import pytz

@receiver(post_save, sender=User)
def create_User(sender, instance, created, **kwargs):
    if created:
        stripeCustomer = stripe.Customer.create(
            name = f"{instance.first_name} - {instance.last_name}",
            email=instance.email,
            metadata={'id':instance.pk} 
        )
        UserInfo.objects.create(user=instance,stripeId=stripeCustomer.get("id"))

@receiver(post_save, sender=Product)
def create_Product(sender, instance, created, **kwargs):
    print('Product WAS CALLED')
    if created:
        product = stripe.Product.create(
            name=instance.name,
            active=instance.isActive,
            description=instance.description,
            metadata={'id':instance.pk}
        )
        instance.stripeId=product.get('id')
        instance.save()
    else:
        product = stripe.Product.modify(
            instance.stripeId,
            name=instance.name,
            active=instance.isActive,
            description=instance.description,
            metadata={'id':instance.pk}
        )

@receiver(post_save, sender=PlanPrice)
def create_PlanPrice(sender, instance, created, **kwargs):
    if created:
        recurring = None
        if instance.paymentType !='onetime':
            recurring={"interval": instance.paymentType}

        planPrice = stripe.Price.create(
            unit_amount_decimal =instance.price*100,
            currency=instance.currency,
            recurring=recurring,
            product=instance.product.stripeId,
            active=instance.isActive,
            nickname=instance.name,
            metadata={'id':instance.pk}
            )

        instance.stripeId=planPrice.get('id')
        instance.save()

@receiver(post_save, sender=Subscription)
def create_Subscription(sender, instance, created, **kwargs):
    return
    if created:
        subscription = stripe.Subscription.create(
            customer=instance.user.info.stripeId,
            items=[
                {"price": instance.planPrice.stripeId},
            ],
            add_invoice_items=[
                {"price": instance.planPrice.activationPlanPrice.stripeId},
            ],
            default_payment_method=instance.userCard.stripeId,
            metadata={'id':instance.pk}
        )
        Subscription.objects.filter(id=instance.id).update(
            currentPeriodEnd=datetime.datetime.fromtimestamp(subscription.get('current_period_end'),tz=pytz.utc),
            stripeId=subscription.get('id'),
            pricePlanSubscriptionStripeId=subscription['items']['data'][0]['id']
        )
    else:

        subscription = stripe.Subscription.modify(
            instance.stripeId,
            proration_behavior='create_prorations',
            items=[
                {   
                    'id': instance.pricePlanSubscriptionStripeId,
                    "price": instance.planPrice.stripeId
                }
            ],

            default_payment_method=instance.userCard.stripeId 
        )

        Subscription.objects.filter(id=instance.id).update(
            currentPeriodEnd=datetime.datetime.fromtimestamp(subscription.get('current_period_end'),tz=pytz.utc),
            stripeId=subscription.get('id'),
            pricePlanSubscriptionStripeId=subscription['items']['data'][0]['id']
        )