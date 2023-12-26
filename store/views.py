from django.shortcuts import render, redirect, get_object_or_404
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
    print("user", user)
    print("order", order)
    print("items", items)

    # If you need to add new products to the order, you would do it here.
    # For example, adding a product to the order:
    # new_product = Product.objects.get(id=some_product_id)
    # OrderItems.objects.create(product=new_product, order=order)

    context = {'items': items, 'order': order}
    return render(request, 'store/cart.html', context)


def add_cart(request, product_id):
    user = request.user.customer
    product = get_object_or_404(Product, id=product_id)
    '''
    this doesnot raise error when product is not there and this raise error(product = Product.objects.get(id=product_id)
    '''
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
        print("cart_item:", cart_item)
        print("done")

    return redirect('/')

# can do this in models and call directly like cartitem.click() then all same other


def click(request, item_id):  # while clicking it calls thisfunction
    cart_item = get_object_or_404(OrderItems, id=item_id)
    cart_item.quantity += 1
    cart_item.save()

    return redirect('/cart')


def unclick(request, item_id):
    cart_item = get_object_or_404(OrderItems, id=item_id)
    if cart_item.quantity > 0:
        cart_item.quantity -= 1
        cart_item.save()

        return redirect('/cart')
    # Redirect to some page, e.g., the cart overview page


def checkout(request):
    user = request.user.customer
    order, created = Order.objects.get_or_create(customer=user, complete=False)
    '''
    iif there is not order or multiple order it raise error(order = Order.objects.get(customer=user, complete=False):)
    but the upper one get_or_create doesnot raise erroe instead of error it create order if doesnot exits
    '''
    item = order.orderitems_set.all()

    context = {'items': item, 'order': order}

    return render(request, 'store/checkout.html', context)
