from django.conf import settings

import paypalrestsdk

paypal = paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": settings.CLIENT_ID,
  "client_secret": settings.PAYPAL_SECREY })


def getPaypalSDK():
    return paypal