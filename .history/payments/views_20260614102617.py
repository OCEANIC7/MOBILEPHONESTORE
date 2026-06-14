from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from orders.models import Order, Cart, CartItem
from accounts.models import Customer
from delivery.models import Delivery
from products.models import Brand
from .models import Payment
import uuid

def get_brands():
    return Brand.objects.all()


@login_required(login_url='/accounts/login/')
def payment(request):
    order_id = request.session.get('order_id')
    payment_method = request.session.get('payment_method')

    if not order_id:
        return redirect('cart')

    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        # Create Payment record
        transaction_ref = str(uuid.uuid4()).upper()[:12]

        Payment.objects.create(
            Order=order,
            Amount=order.GrandTotal,
            PaymentMethod=payment_method,
            PaymentStatus='Completed',
            TransactionReference=transaction_ref,
        )

        # Update Order Status
        order.OrderStatus = 'Paid'
        order.save()

        # Update Delivery Status
        delivery = get_object_or_404(Delivery, Order=order)
        delivery.DeliveryStatus = 'Preparing'
        delivery.save()

        # Clear the cart
        customer = get_object_or_404(Customer, User=request.user)
        cart_obj = Cart.objects.filter(Customer=customer).first()
        if cart_obj:
            CartItem.objects.filter(Cart=cart_obj).delete()

        # Clear session
        del request.session['order_id']
        del request.session['payment_method']

        return redirect('order_success')

    return render(request, 'payments/payment.html', {
        'order': order,
        'payment_method': payment_method,
        'brands': get_brands(),
    })


@login_required(login_url='/accounts/login/')
def order_success(request):
    return render(request, 'payments/order_success.html', {
        'brands': get_brands(),
    })


@login_required(login_url='/accounts/login/')
def my_orders(request):
    customer = get_object_or_404(Customer, User=request.user)
    orders = Order.objects.filter(Customer=customer).order_by('-OrderDate')

    orders_data = []
    for order in orders:
        payment = Payment.objects.filter(Order=order).first()
        delivery = Delivery.objects.filter(Order=order).first()
        orders_data.append({
            'order': order,
            'payment': payment,
            'delivery': delivery,
        })

    return render(request, 'payments/my_orders.html', {
        'orders_data': orders_data,
        'brands': get_brands(),
    })