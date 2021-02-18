from paypalrestsdk import CreditCard
from ..paypalSDK import getPaypalSDK
getPaypalSDK()
import logging
logging.basicConfig(level=logging.INFO)


class PaypalVault:

    @staticmethod
    def createCard(card):
        credit_Card = CreditCard(card)
        credit_Card.create()