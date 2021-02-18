import braintree

gateway = braintree.BraintreeGateway(
  braintree.Configuration(
    environment=braintree.Environment.Sandbox,
    merchant_id='',
    public_key='',
    private_key=''
  )
)


class BrainTreeVault:

  @staticmethod
  def addCustomerBillingInfo(customer):
    result = gateway.customer.create(customer)

    return result


  @staticmethod
  def addCustomerCard(customer_id, card):
    card['customer_id'] = customer_id
    result= gateway.credit_card.create(card)

    return result

  @staticmethod
  def getCustomer(customer_id):
    return gateway.customer.find(customer_id)