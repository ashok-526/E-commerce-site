from django.urls import path, include

from .views import *


urlpatterns = [
    path('', store, name='store'),

    path('cart/', cart, name='cart'),
    path("checkout/", checkout, name='checkout'),
    path('add-card/<obj_uid>', cart , name='add-card'),
]
