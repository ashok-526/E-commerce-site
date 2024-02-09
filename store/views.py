from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth.models import User
import datetime
import stripe
# Create your views here.

def store(request):
    # Initialize variables
    product = Product.objects.all()
    order = None
    cart_item = 0

    if request.user.is_authenticated:
        user = request.user.customer
        order, _ = Order.objects.get_or_create(customer=user, complete=False)
        items = order.orderitems_set.all()
        cart_item = order.get_cart_quantity
    else:

        items = []

    context = {'product': product, 'cart_item': cart_item,
               'order': order, 'items': items}
    return render(request, 'store/store.html', context)


def cart(request):
    # Initialize default values
    items = []
    order = None
    cart_item = 0

    if request.user.is_authenticated:
        user = request.user.customer
        order, _ = Order.objects.get_or_create(customer=user, complete=False)
        items = order.orderitems_set.all()
        cart_item = order.get_cart_quantity
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_quantity': 0}
        # For non-authenticated users, you can decide how to handle this.
        # For example, show a message indicating the cart is empty or that they need to log in.
        # You can also redirect them to a login page or another appropriate page.

    context = {'items': items, 'order': order, 'cart_item': cart_item}
    return render(request, 'store/cart.html', context)


def add_cart(request, product_id):
    if request.user.is_authenticated:
        user = request.user.customer
        print(user)
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

        messages.success(request, "Item added to cart successfully.")
        return redirect('/')  # Assuming you have a URL named 'cart'
    else:
        # For non-authenticated users, redirect to login page or show a message
        messages.info(request, "Please log in to add items to the cart.")
        return redirect('/')  # Assuming you have a URL named 'login'
# can do this in models and call directly like cartitem.click() then all same other


def click(request, item_id):
    cart_item = get_object_or_404(OrderItems, id=item_id)
    if cart_item.quantity > 0:
        cart_item.quantity += 1
        cart_item.save()

        return redirect('/cart')


def unclick(request, item_id):
    cart_item = get_object_or_404(OrderItems, id=item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()

    elif cart_item.quantity == 1:
        cart_item.delete()

    return redirect('/cart')


def checkout(request):
    items = []
    cart_item = 0
    order = None

    if request.user.is_authenticated:
        user = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=user, complete=False)
        items = order.orderitems_set.all()
        print(items)
        cart_item = order.get_cart_quantity
        cart_total = order.get_cart_total
        shipping = order.shipping
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_quantity': 0}
        # For non-authenticated users, you might want to redirect them
        # to the login page or handle the checkout for guest users differently.
        # Redirect to login as an example:
      # Assuming you have a URL named 'login'

    if request.method == 'POST':
        Address = request.POST.get("address")
        city = request.POST.get("city")
        zipcode = request.POST.get("zipcode")
        state = request.POST.get("state")

        if request.user.is_authenticated and shipping != False:
            customer = request.user.customer
            order = order
            ShippingAddress.objects.create(
                order=order,
                customer=customer,
                Address=Address,
                city=city,
                zipcode=zipcode,
                state=state
            )

    context = {'items': items, 'order': order, 'cart_item': cart_item}
    return render(request, 'store/checkout.html', context)


from stripe.error import CardError

def payment_process(request):
    if request.user.is_authenticated:
        user = request.user.customer
        order, created = Order.objects.get_or_create(customer=user, complete=False)
        amount = order.get_cart_total  # Ensure this is in cents for Stripe

        stripe.api_key = "sk_test_51Nrdg6HOKyBJ9R4uHTuykRR1HVr2ZXWpipXWiyLWCT5RhNEvyUK3BkJOJBkTi6IT3t38tBSnKF1IkcXRDAuuJNwV00qO8ArHUg"

        # Ensure you have a Stripe customer ID associated with your user
        stripe_customer_id = user.stripe_customer_id  # Replace with your way of storing/fetching the Stripe customer ID

        if not stripe_customer_id:
            # Create a Stripe Customer if not exists
            customer = stripe.Customer.create(
                email=user.email,
                # other details
            )
            stripe_customer_id = customer.id
            # Store this customer ID in your database for future reference

        try:
            # Create a PaymentIntent with the Stripe Customer ID
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                customer=stripe_customer_id,
                payment_method=request.POST.get('payment_method_id'),
                confirm=True,
            )

            if intent.status == 'succeeded':
                # Handle post-payment fulfillment
                order.complete = True
                order.save()
                return redirect('/success_page')

        except stripe.error.StripeError as e:
            # Handle Stripe exceptions appropriately
            print(e)

    return render(request, 'payment.html')


