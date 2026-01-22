from click_up import ClickUp
from core import settings
from .serializers import OrderSerializer
from asgiref.sync import sync_to_async
from paytechuz.gateways.payme import PaymeGateway
from django.conf import settings


click_up = ClickUp(
    service_id=settings.CLICK_SERVICE_ID,
    merchant_id=settings.CLICK_MERCHANT_ID,
)



def _send_payment_url(data: dict):
    serializer_class = OrderSerializer
    serializer = serializer_class(data=data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    paytechuz_settings = settings.PAYTECHUZ
    payment_url = None
    if serializer.data['payment_method'] == 'payme':
        payme = PaymeGateway(
            payme_id=paytechuz_settings['PAYME']['PAYME_ID'],
            payme_key=paytechuz_settings['PAYME']['PAYME_KEY'],
            is_test_mode=paytechuz_settings['PAYME']['IS_TEST_MODE']
        )
        payment_url = payme.create_payment(
            id=serializer.data['id'],
            amount=serializer.data['cost'],
            return_url="https://t.me/phd_tv_bot",
            account_field_name=paytechuz_settings['PAYME']['ACCOUNT_FIELD'],
        )
    elif serializer.data['payment_method'] == 'click':
        payment_url = click_up.initializer.generate_pay_link(
            id=serializer.data['id'],
            amount=serializer.data['cost'],
            return_url="https://t.me/phd_tv_bot"
        )

    return {'payment_url': payment_url}

send_link_for_payment = sync_to_async(_send_payment_url)
