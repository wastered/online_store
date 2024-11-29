import ipaddress
import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from ...orders.models import Order
from ..tasks import payment_completed

IPS = [
    ipaddress.IPv4Network('185.71.76.0/27'),
    ipaddress.IPv4Network('185.71.77.0/27'),
    ipaddress.IPv4Network('77.75.153.0/25'),
    ipaddress.IPv4Network('77.75.156.11'),
    ipaddress.IPv4Network('77.75.156.35'),
    ipaddress.IPv4Network('77.75.154.128/25'),
    ipaddress.IPv6Network('2a02:5180::/32'),
    ipaddress.IPv4Network('127.0.0.1'),
]


def check_ip_in_networks(ip: str) -> bool:
    ip_obj = ipaddress.ip_address(ip)
    for network in IPS:
        if ip_obj in network:
            return True
    return False


@csrf_exempt
def yk_webhook(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if not check_ip_in_networks(ip):  # Проверка IP адреса
        return HttpResponse(status=400)

    data = json.loads(request.body)
    payment_status = data['status']
    test = data['test']

    if payment_status == 'succeeded' and test is False:
        print(11111111111)
        order_id = data['metadata'].get('order_id')
        order = Order.objects.filter(id=order_id).first()
        print(f"{order=}")
        if order:
            order.paid = True
            order.yookassa_id = data['id']
            order.save()

            # запустить асинхронное задание
            payment_completed.delay(order.id)
            return HttpResponse(status=200)
    return HttpResponse(status=400)
