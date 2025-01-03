from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login ,logout
from django.db.models import Sum
from django.contrib.auth.models import User
import datetime
import stripe
import requests
# Create your views here.


# def login(request):
#     if request.method=='POST':
#         username=request.POST.get('username')
#         password=request.get('password')

#         user= User.objects.filter(username=username).first()

#         if not user:
#             messages.error("User name doesnot exist!")
#             return redirect('/login/')
#         else

#     return render(request , 'store/login.html')
def login(request):
    # Check if the user is already logged in
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in!")
        return redirect('/')  # Redirect to homepage or any other page

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Invalid username or password!")
            return redirect('login')

    return render(request, 'store/login.html')
def register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Basic validation
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already used!")
            return redirect('register')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            Customer.objects.create(user=user, name=username, email=email)  # Ensure fields match your Customer model

            messages.success(request, "Account created successfully! Please log in.")
            return redirect('login')

    return render(request, 'store/register.html')

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

def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')  # Replace 'login' with the name of your login URL

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




# from stripe.error import CardError

# def payment_process(request):
#     if request.user.is_authenticated:
#         user = request.user.customer
#         order, created = Order.objects.get_or_create(customer=user, complete=False)
#         amount = order.get_cart_total  # Ensure this is in cents for Stripe

#         stripe.api_key = "sk_test_51Nrdg6HOKyBJ9R4uHTuykRR1HVr2ZXWpipXWiyLWCT5RhNEvyUK3BkJOJBkTi6IT3t38tBSnKF1IkcXRDAuuJNwV00qO8ArHUg"

#         # Ensure you have a Stripe customer ID associated with your user
#         stripe_customer_id = user.stripe_customer_id  # Replace with your way of storing/fetching the Stripe customer ID

#         if not stripe_customer_id:
#             # Create a Stripe Customer if not exists
#             customer = stripe.Customer.create(
#                 email=user.email,
#                 # other details
#             )
#             stripe_customer_id = customer.id
#             # Store this customer ID in your database for future reference

#         try:
#             # Create a PaymentIntent with the Stripe Customer ID
#             intent = stripe.PaymentIntent.create(
#                 amount=amount,
#                 currency='usd',
#                 customer=stripe_customer_id,
#                 payment_method=request.POST.get('payment_method_id'),
#                 confirm=True,
#             )

#             if intent.status == 'succeeded':
#                 # Handle post-payment fulfillment
#                 order.complete = True
#                 order.save()
#                 return redirect('/success_page')

#         except stripe.error.StripeError as e:
#             # Handle Stripe exceptions appropriately
#             print(e)

#     return render(request, 'payment.html')

import uuid
from django.shortcuts import render

def Esewa(request):
    user = request.user.customer
   
    # Get the cart and calculate total
    order, _ = Order.objects.get_or_create(customer=user, complete=False)
    total = order.get_cart_total
    qt=order.get_cart_quantity

    # Generate a UUID
    uid = uuid.uuid4()
    
    # Pass total and uid to the template context
    context = {'total1': total, 'uid': uid, 'qt' : qt}

    # Only proceed if the request is a POST request
    if request.method == "POST":
        url = "https://uat.esewa.com.np/epay/transrec"
        data = {
            'amt': total,
            'scd': 'EPAYTEST',
            'rid': request.GET.get('refid'),
            'pid': uid
        }
        
        resp = requests.post(url, data=data)
        
        if resp.status_code == 200 and resp.text == 'success':
            # Perform the following actions within a transaction
                # Add cart items to the cart
                # (Assuming you have a method to add items to the cart)
                # cart.add_items(...) 
                
                # Mark the cart as paid and save it
                if not order.complete:
                    order.complete = True
                    order.esewa = request.GET.get('oid')
                    order.save()

            # Redirect after successful payment
                return redirect("/")  # replace "success_url" with your success URL

    # Render the payment template with the context
    return render(request, 'store/payment.html', context)

