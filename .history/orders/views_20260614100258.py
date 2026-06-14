from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from products.models import Product, Brand
from accounts.models import Customer
from .models import Cart, CartItem, Order, ShippingZone

def get_brands():
    return Brand.objects.all()


@login_required(login_url='/accounts/login/')
def cart(request):
    customer = get_object_or_404(Customer, User=request.user)
    cart_obj, created = Cart.objects.get_or_create(Customer=customer)
    items = CartItem.objects.filter(Cart=cart_obj)

    product_total = sum(item.Product.Price * item.Quantity for item in items)

    return render(request, 'orders/cart.html', {
        'items': items,
        'product_total': product_total,
        'brands': get_brands(),
    })


@login_required(login_url='/accounts/login/')
def add_to_cart(request, product_id):
    if request.method == 'POST':
        customer = get_object_or_404(Customer, User=request.user)
        product = get_object_or_404(Product, id=product_id)
        cart_obj, created = Cart.objects.get_or_create(Customer=customer)

        item, item_created = CartItem.objects.get_or_create(Cart=cart_obj, Product=product)
        if not item_created:
            item.Quantity += 1
            item.save()

    return redirect('cart')


@login_required(login_url='/accounts/login/')
def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        item.Quantity = quantity
        item.save()
    else:
        item.delete()

    return redirect('cart')


@login_required(login_url='/accounts/login/')
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart')

@login_required(login_url='/accounts/login/')
def checkout(request):
    customer = get_object_or_404(Customer, User=request.user)
    cart_obj = get_object_or_404(Cart, Customer=customer)
    items = CartItem.objects.filter(Cart=cart_obj)

    if not items:
        return redirect('cart')

    zones = ShippingZone.objects.all()
    product_total = sum(item.Product.Price * item.Quantity for item in items)

    if request.method == 'POST':
        zone_id = request.POST.get('zone')
        address = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        zone = get_object_or_404(ShippingZone, id=zone_id)
        shipping_cost = zone.DeliveryCost
        grand_total = product_total + shipping_cost

        # Create Order
        order = Order.objects.create(
            Customer=customer,
            ProductTotal=product_total,
            ShippingCost=shipping_cost,
            GrandTotal=grand_total,
            OrderStatus='Awaiting Payment',
        )

        # Save delivery info
        from delivery.models import Delivery
        Delivery.objects.create(
            Order=order,
            DeliveryAddress=address,
            ShippingZone=zone,
            DeliveryStatus='Not Eligible',
        )

        # Save payment method choice to session
        request.session['payment_method'] = payment_method
        request.session['order_id'] = order.id

        return redirect('payment')

    return render(request, 'orders/checkout.html', {
        'items': items,
        'zones': zones,
        'product_total': product_total,
        'brands': get_brands(),
    })