from django.db import models
from django.contrib.auth.models import User

class Customer(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()  # Using DecimalField
    image = models.ImageField(upload_to='product-image', null=True, blank=True)
    digital = models.BooleanField(default=False, null=True, blank=False)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True)
    date_order = models.DateTimeField(auto_now_add=True)  # Corrected field name
    complete = models.BooleanField()
    transaction_id = models.CharField(max_length=50)  # Corrected field name

    def __str__(self):
        return str(self.customer)

    @property
    def get_cart_total(self):
        return sum(item.get_total for item in self.orderitems_set.all())

    @property
    def get_cart_quantity(self):
        return sum(item.quantity for item in self.orderitems_set.all())

    @property
    def shipping(self):
        return any(not item.product.digital for item in self.orderitems_set.all())

class OrderItems(models.Model):  # Note: Class name should be singular
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # This will now reference the order's customer if present
        return f"OrderItem {self.id} for {self.order.customer if self.order and self.order.customer else 'Unknown'}"

    @property
    def get_total(self):
        return self.product.price * self.quantity if self.product else 0


class ShippingAddress(models.Model):
    customer = models.ForeignKey(
        Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=100)  # Corrected field name
    city = models.CharField(max_length=50)
    zipcode = models.CharField(max_length=15)  # Using CharField for zip codes
    state = models.CharField(max_length=20)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
