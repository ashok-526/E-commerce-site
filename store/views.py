from django.shortcuts import render
from .models import *
from django.db.models import Sum
from django.contrib.auth.models import User
# Create your views here.


def store(request):
    product = Product.objects.all()
    context = {'product': product}
    return render(request, 'store/store.html', context)


def cart(request,obj):
    user = request.user.customer
    order , created =Order.objects.get_or_create(customer=user , complete = False)
    item= order.orderitems_set.all(uid=obj)
    orderitems=OrderItems.objects.create(
        product=order , created,
        order=items
        )
    context={'items':item, 'order':order}


    return render(request, 'store/cart.html',context)


def checkout(request):
    user = request.user.customer
    order , created =Order.objects.get_or_create(customer=user , complete = False)
    item= order.orderitems_set.all()

    context={'items':item, 'order':order}

    return render(request, 'store/checkout.html',context)
