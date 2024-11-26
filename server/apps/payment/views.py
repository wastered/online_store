from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from yookassa import Configuration, Payment
from yookassa.domain.exceptions import BadRequestError

from server.settings.components.common import YOOKASSA_ACCOUNT_ID, YOOKASSA_SECRET_KEY
from ..orders.models import Order

# данные для Yookassa
Configuration.account_id = YOOKASSA_ACCOUNT_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY


def payment_process(request):
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        return_url = request.build_absolute_uri(reverse('payment:completed'))
        total_price = sum(item.price * item.quantity for item in order.items.all())

        #  данные для оформления платежа
        payment_data = {
            "amount": {
                "value": total_price,
                "currency": "RUB"
            },
            "capture": True,
            "description": f"Order №{order.id}",
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "metadata": {
                'order_id': order.id
            }
        }

        try:
            payment_info = Payment.create(payment_data)
        except (BadRequestError, ValueError):
            return redirect("payment:canceled")

        return redirect(payment_info.confirmation.confirmation_url, code=303)
    else:
        return render(request, "payment/process.html", locals())


def payment_completed(request):
    return render(request, 'payment/completed.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')
