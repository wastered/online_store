from io import BytesIO

import weasyprint
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from ..orders.models import Order
from ...settings.components.common import STATIC_ROOT


@shared_task
def payment_completed(order_id):
    """
    Задание по отправке уведомлений по электронной почте
    при успешном оплате заказа.
    """
    order = Order.objects.get(id=order_id)
    # Создание счета e-mail
    subject = f"My Shop – Invoice no.{order.id}"
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(subject, message, 'admin@myshop.com',
                         [order.email])

    # сгенерировать PDF
    html = render_to_string('orders/order/pdf.html', {"order": order})
    out = BytesIO()
    stylesheets = weasyprint.CSS(STATIC_ROOT / 'orders/css/pdf.css')
    weasyprint.HTML(string=html).write_pdf(out, stylesheets=[stylesheets])

    # прикрепить PDF-файл
    email.attach(f"order_{order.id}.pdf", out.getvalue(), mimetype='application/pdf')

    # отправить электронное письмо
    email.send()
