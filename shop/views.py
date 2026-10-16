import time
from django.db import transaction
from django.db.models import F
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Order, OrderItem



@api_view(['POST'])
def purchase_naive(request, pk):
    product = Product.objects.get(pk=pk)
    if product.stock <= 0:
        return Response({"detail": "Out of stock"}, status=400)

    time.sleep(0.05)

    order = Order.objects.create()
    OrderItem.objects.create(order=order, product=product, quantity=1)

    product.stock -= 1
    product.save()
    return Response({"detail": "Purchase successful"}, status=200)



@api_view(['POST'])
def purchase_atomic_only(request, pk):
    with transaction.atomic():
        product = Product.objects.get(pk=pk)
        if product.stock <= 0:
            return Response({"detail": "Out of stock"}, status=400)

        time.sleep(0.05)

        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)

        product.stock -= 1
        product.save()
        return Response({"detail": "Purchase successful"}, status=200)



@api_view(['POST'])
def purchase_with_lock(request, pk):
    with transaction.atomic():
        product = Product.objects.select_for_update().get(pk=pk)
        if product.stock <= 0:
            return Response({"detail": "Out of stock"}, status=400)

        time.sleep(0.05)

        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)

        product.stock -= 1
        product.save()
        return Response({"detail": "Purchase successful"}, status=200)



@api_view(['POST'])
def purchase_atomic_f_update(request, pk):
    with transaction.atomic():
        rows_affected = Product.objects.filter(pk=pk, stock__gt=0).update(stock=F('stock') - 1)

        if rows_affected == 1:
            order = Order.objects.create()
            OrderItem.objects.create(order=order, product_id=pk, quantity=1)
            return Response({"detail": "Purchase successful"}, status=200)
        else:
            return Response({"detail": "Out of stock"}, status=400)