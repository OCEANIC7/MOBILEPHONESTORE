from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import Customer
from orders.models import Order
from .models import Delivery
from products.models import Brand

def get_brands():
    return Brand.objects.all()


@login_required(login_url='/accounts/login/')
def delivery_tracking(request):
    customer = get_object_or_404(Customer, User=request.user)
    orders = Order.objects.filter(Customer=customer).order_by('-OrderDate')

    tracking_data = []
    for order in orders:
        delivery = Delivery.objects.filter(Order=order).first()
        tracking_data.append({
            'order': order,
            'delivery': delivery,
        })

    return render(request, 'delivery/tracking.html', {
        'tracking_data': tracking_data,
        'brands': get_brands(),
    })