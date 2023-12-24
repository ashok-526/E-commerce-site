from django.shortcuts import render
from .models import *
from django.db.models import Sum
from django.contrib.auth.models import User
# Create your views here.


def store(request):
    product = Product.objects.all()
    context = {'product': product}
    return render(request, 'store/store.html', context)


def cart(request):
    user = request.user.customer
    order, _ = Order.objects.get_or_create(customer=user, complete=False)
    items = order.orderitems_set.all()

    # If you need to add new products to the order, you would do it here.
    # For example, adding a product to the order:
    # new_product = Product.objects.get(id=some_product_id)
    # OrderItems.objects.create(product=new_product, order=order)

    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)

def checkout(request):
    user = request.user.customer
    order , created =Order.objects.get_or_create(customer=user , complete = False)
    item= order.orderitems_set.all()

    context={'items':item, 'order':order}

    return render(request, 'store/checkout.html',context)
