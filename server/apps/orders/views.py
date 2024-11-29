import weasyprint
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse

from .forms import OrderCreateForm
from .models import OrderItem, Order
from .tasks import order_created
from ..cart.cart import Cart
from ...settings.components.common import STATIC_ROOT


def order_create(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            order = form.save()
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
            order.save()

            for item in cart:
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'],
                                         quantity=item['quantity'])
                # Очистить корзину
                cart.clear()

                # запустить асинхронное задание
                order_created.delay(order.id)

                # задать заказ в сеансе
                request.session['order_id'] = order.id

                # перенаправить к платежу
                return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()

    return render(request,
                  'orders/order/create.html',
                  context={
                      'cart': cart,
                      'form': form,
                  })


@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html',
                  context={
                      'order': order,
                  })


@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    html = render_to_string('orders/order/pdf.html',
                            {'order': order})
    response = HttpResponse(html, content_type='application/pdf')
    response['Content-Disposition'] = f"filename=order_{order_id}.pdf"
    weasyprint.HTML(string=html).write_pdf(response, stylesheets=[weasyprint.CSS(STATIC_ROOT / 'orders/css/pdf.css')])

    return response
