from django.shortcuts import render,redirect, get_object_or_404
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
    print("user",user)
    print("order",order)
    print("items",items)

    # If you need to add new products to the order, you would do it here.
    # For example, adding a product to the order:
    # new_product = Product.objects.get(id=some_product_id)
    # OrderItems.objects.create(product=new_product, order=order)

    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)
def add_cart(request, product_id):
    user = request.user.customer
    product = get_object_or_404(Product, id=product_id)
    order, _ = Order.objects.get_or_create(customer=user, complete=False)

    # Find an existing cart item or create a new one
    cart_item, created = OrderItems.objects.get_or_create(
        product=product,
        order=order,
        defaults={'quantity': 1}  # Default quantity if new
    )
    if not created:
        cart_item.quantity += 1  # Increment quantity if item exists
        cart_item.save()
        print("cart_item:",cart_item)
        print("done")


    # Redirect to some page, e.g., the cart overview page
    return redirect('/')
def checkout(request):
    user = request.user.customer
    order , created =Order.objects.get_or_create(customer=user , complete = False)
    item= order.orderitems_set.all()

    context={'items':item, 'order':order}

    return render(request, 'store/checkout.html',context)
