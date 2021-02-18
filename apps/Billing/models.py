from django.db import models
from django.db.models.signals import post_save
from libs.braintreesdk.vault import BrainTreeVault

# Create your models here.

class BillingProfile(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name="billing_profile")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Cards(models.Model):
    braintree_token = models.CharField(max_length=250)
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE, related_name="cards")
    customer_id = models.CharField(max_length=100)
    card_holder_name = models.CharField(max_length=250)
    card_type = models.CharField(max_length=25)
    last_four = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    selected = models.BooleanField(default=False)

    def __str__(self):
        return self.card_holder_name
    
    def braintree_customer(self):
        customer = BrainTreeVault.getCustomer(self.customer_id)
        return customer


# def postSaveCards(sender, instance):
    
