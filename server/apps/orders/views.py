from django.urls import reverse
from django.shortcuts import render, redirect

from .forms import OrderCreateForm
from .models import OrderItem
from .tasks import order_created
from ..cart.cart import Cart


def order_create(request):
    cart = Cart(request)

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            order = form.save()

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
