from asgiref.sync import async_to_sync
from click_up.views import ClickWebhook
from click_up.models import ClickTransaction
from paytechuz.integrations.django.views import BasePaymeWebhookView

from keyboards.inline import group_link_button
from loader import bot, db
from product.models import Order


async def send_url_func(user_tg_id, url):
    """Foydalanuvchiga film URL ni yuborish"""
    await bot.send_message(
        chat_id=user_tg_id,
        text="Kinoni ko'rish uchun pastgi tugmachani bo'sing 👇",
        reply_markup=await group_link_button(url),
        protect_content=True,
    )
    await bot.session.close()

send_url_to_user = async_to_sync(send_url_func)


class PaymeWebhookView(BasePaymeWebhookView):

    def successfully_payment(self, params, transaction_obj):
        order = Order.objects.get(id=transaction_obj.account_id)
        order.is_paid = True
        order.save()
        if order.count == 1:
            product = order.product.first()
            if product:
                # Resolution ga qarab URL olish
                if order.resolution == "4k":
                    url = product.group_url_4k
                else:
                    url = product.group_url_1080p

                # Foydalanuvchiga yuborish
                if url:
                    send_url_to_user(order.user.tg_id, url)


    def cancelled_payment(self, params, transaction_obj):
        order = Order.objects.get(id=transaction_obj.account_id)
        order.is_paid = False
        order.save()



class ClickWebhookAPIView(ClickWebhook):
    def successfully_payment(self, params):
        """
        successfully payment method process you can ovveride it
        """
        transaction = ClickTransaction.objects.get(
            transaction_id=params.click_trans_id
        )
        order = Order.objects.get(id=transaction.account_id)
        order.is_paid = True
        order.save()
        if order.count == 1:
            product = order.product.first()
            if product:
                # Resolution ga qarab URL olish
                if order.resolution == "4k":
                    url = product.group_url_4k
                else:
                    url = product.group_url_1080p

                # Foydalanuvchiga yuborish
                if url:
                    send_url_to_user(order.user.tg_id, url)

    def cancelled_payment(self, params):
        """
        cancelled payment method process you can ovveride it
        """
        transaction = ClickTransaction.objects.get(
            transaction_id=params.click_trans_id
        )
        if transaction.state == ClickTransaction.CANCELLED:
            order = Order.objects.get(id=transaction.account_id)
            order.is_paid = False
            order.save()

