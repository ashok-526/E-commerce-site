from django.urls import path, include

from .views import *


urlpatterns = [
    path('', store, name='store'),
    path('add-cart/<int:product_id>/', add_cart, name='add-cart'),
    path('cart/', cart, name='cart'),
    path("checkout/", checkout, name='checkout'),

]
