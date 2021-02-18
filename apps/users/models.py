from django.db import models
from apps.address.models import Address
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager)
from django.core.mail import send_mail
from apps.stores.models import Store
from apps.address.models import Address
from django.db.models.signals import post_save, pre_save
from .utils import TokenGenerator
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils import timezone
from django.conf import settings
from django_currentuser.middleware import (
    get_current_user, get_current_authenticated_user)
from services.emailService.send_email import sendEmail
from apps.order.dynamodb import create_in_dynamodb
import json
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
            """
            Creates and saves a User with the given email and password.
            """
            if not email:
                raise ValueError('Users must have an email address')

            user = self.model(
                email=self.normalize_email(email),
            )

            user.set_password(password)
            user.save(using=self._db)
            return user


    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=80, blank=True)
    email = models.EmailField(max_length=250, unique=True)
    active = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    token = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=10) 

    USERNAME_FIELD = 'email'

    def get_full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name

    def __str__(self):          
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin
    
    @property
    def is_staff(self):
        return True

    @property
    def is_active(self):
        "Is the user active?"
        return self.active

    @property
    def selected_address(self):
        try:
            return self.delivery_info.get(selected=True)
        except:
            return None

    objects = UserManager()

def set_token(sender, instance, **kwargs):
    account_activation_token = TokenGenerator()
    instance.token = account_activation_token.make_token(instance)

pre_save.connect(set_token, sender=User)

def send_activation_email(sender, instance, **kwargs):
    if not instance.is_admin and not instance.is_active:
        mail_subject = 'Activa tu cuenta en pacome.'
        current_site = 'pacomeapp.com'
        to_email = instance.email
        message = render_to_string('acc_active_email.html', {
            'user': instance,
            'domain': settings.HOSTNAME,
            'uid':urlsafe_base64_encode(force_bytes(instance.id)).decode(),
            'token':instance.token,
        })
        
        emailObject = {
            "email": {
                "html_body": message,
                "subject": mail_subject
            },
             "toEmail": to_email,
             "fromEmail": "info@pacomeapp.com"
        }
        sendEmail(emailObject)
     

post_save.connect(send_activation_email, sender=User)

class Preferences(models.Model):
    account = models.ForeignKey(User, on_delete=models.CASCADE, related_name="account_preference")
    fav_stores = models.ManyToManyField('address.StoreLocations')


class StoreManagerProfile(models.Model):
    ProfileType = ((1, 'store_owner'), (2, 'store_staff'), (3, 'delivery boy'), (4, 'admin'))
    role = models.PositiveSmallIntegerField(default=2, choices=ProfileType)
    store = models.ForeignKey('address.StoreLocations', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stores_manager_profile")
    date_joined = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    checked_notifications = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{} {}".format(self.user.first_name, self.role)

    @property
    def role_str(self):
        type = dict(self.ProfileType)
        return type[self.role]

def store_manager_presave(sender, instance, **kwargs):
    connection_data = {"user_id": instance.user.email, "identifiers_id": [str(instance.store.id)], "user_info":{"user_role": "1"}}
    create_in_dynamodb(connection_data, "AuthTableStag")
pre_save.connect(store_manager_presave, sender=StoreManagerProfile)


class StoreOutdoorSellerProfile(models.Model):
    OUTDOOR_SELLER_TYPE = (
        (1, 'street_stablishment'),
        (2, 'door_to_door'),
        (3, 'nomada')
    )
    store = models.ForeignKey('address.StoreLocations', on_delete=models.SET_NULL, null=True, related_name="outdoor_sellers")
    product_sells = models.ManyToManyField('products.Product', related_name="outdoor_sellers_in_stock")
    outdoor_seller_type = models.PositiveSmallIntegerField(choices=OUTDOOR_SELLER_TYPE, default=1)
    cedula = models.CharField(max_length=11, null=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)


    def __str__(self):
        return f"{self.store.store.name} {self.outdoor_seller_type} {self.cedula}"
   
    @property
    def is_public(self):
        return (self.store.store.store_type == 4)

