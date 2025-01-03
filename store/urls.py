from django.urls import path, include

from .views import *


urlpatterns = [
    path('', store, name='store'),
    path('login/',login,name='login'),
    path('register/',register,name='register'),
    path('payment/', Esewa , name = 'payment'),
    path('add-cart/<int:product_id>/', add_cart, name='add-cart'),
    path('click/<int:item_id>/', click, name='click'),
    path('unclick/<int:item_id>/', unclick, name='unclick'),
    path('cart/', cart, name='cart'),
    path("checkout/", checkout, name='checkout'),
    path('click/<int:item_id>/', click, name='click'),
     path('logout/', logout_view, name='logout'),
    path('unclick/<int:item_id>/', unclick, name='unclick'),
   # path('login/', login , name='login')


]
