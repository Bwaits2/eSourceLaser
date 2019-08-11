import decimal
from pinax.stripe.actions import charges
from pinax.stripe.actions.sources import create_card, delete_card
from djmoney.utils import get_amount


def charge(request, quote, token):

    print(get_amount(quote.total))

    create_card(request.user.customer, token)
    return charges.create(amount=decimal.Decimal(get_amount(quote.total)), customer=request.user.customer.stripe_id)
