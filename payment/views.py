from asgiref.sync import async_to_sync
from click_up.views import ClickWebhook
from click_up.models import ClickTransaction
from paytechuz.integrations.django.views import BasePaymeWebhookView

from keyboards.inline import group_link_button
from loader import bot, db
from product.models import Order


async def send_url_func(data):
    count = data["count"]
    resolution = data["resolution"]
    product = data["product"]
    user = data["user"]
    if count == 1:
        pr_data = await db.get_product(product)
        if resolution == "1080p":
            pr_url = pr_data[7]
        else:
            pr_url = pr_data[8]

        await bot.send_message(
            chat_id=user,
            text="Kinoni ko'rish uchun pastgi tugmachani bo'sing",
            reply_markup=await group_link_button(pr_url),
            protect_content=True,
        )

send_url_to_user = async_to_sync(send_url_func)


class PaymeWebhookView(BasePaymeWebhookView):

    def successfully_payment(self, params, transaction_obj):
        order = Order.objects.get(id=transaction_obj.account_id)
        order.is_paid = True
        order.save()
        data = {
            "user": order.user.tg_id,
            "product": order.product,
            "count": order.count,
            "resolution": order.resolution,
        }
        send_url_to_user(data)


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
        data = {
            "user": order.user.tg_id,
            "product": order.product,
            "count": order.count,
            "resolution": order.resolution,
        }
        send_url_to_user(data)

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

