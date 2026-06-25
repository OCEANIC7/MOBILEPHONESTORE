from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from orders.models import Order, Cart, CartItem
from accounts.models import Customer
from delivery.models import Delivery
from products.models import Brand
from .models import Payment, SavedPaymentMethod, MOBILE_MONEY_METHODS, CARD_METHODS
import uuid

def get_brands():
    return Brand.objects.all()


@login_required(login_url='/accounts/login/')
def payment(request):
    order_id = request.session.get('order_id')

    if not order_id:
        return redirect('cart')

    order = get_object_or_404(Order, id=order_id)
    customer = get_object_or_404(Customer, User=request.user)
    saved_methods = SavedPaymentMethod.objects.filter(Customer=customer)

    # Let the user back out to method selection
    if request.method == 'GET' and request.GET.get('change'):
        request.session.pop('payment_method', None)
        return redirect('payment')

    # Stage 1: the user is choosing/confirming a payment method (POST from this page)
    if request.method == 'POST' and 'choose_method' in request.POST:
        chosen_method = request.POST.get('payment_method')
        request.session['payment_method'] = chosen_method
        return redirect('payment')

    payment_method = request.session.get('payment_method')

    # Stage 2: details + final confirmation
    if request.method == 'POST' and 'confirm_payment' in request.POST:
        payment_method = request.session.get('payment_method')
        saved_method_id = request.POST.get('saved_method_id')
        set_default = request.POST.get('set_default') == 'on'

        if saved_method_id:
            # Reusing an existing saved profile
            saved_method = get_object_or_404(SavedPaymentMethod, id=saved_method_id, Customer=customer)
            if set_default and not saved_method.IsDefault:
                saved_method.IsDefault = True
                saved_method.save()
        else:
            # Collecting fresh details for this method
            if payment_method in MOBILE_MONEY_METHODS:
                saved_method = SavedPaymentMethod.objects.create(
                    Customer=customer,
                    PaymentMethod=payment_method,
                    PhoneNumber=request.POST.get('phone_number', '').strip(),
                    IsDefault=set_default,
                )
            else:
                saved_method = SavedPaymentMethod.objects.create(
                    Customer=customer,
                    PaymentMethod=payment_method,
                    BankAccountNumber=request.POST.get('bank_account_number', '').strip(),
                    BankName=request.POST.get('bank_name', '').strip(),
                    IsDefault=set_default,
                )

        # Create Payment record
        transaction_ref = str(uuid.uuid4()).upper()[:12]

        Payment.objects.create(
            Order=order,
            Amount=order.GrandTotal,
            PaymentMethod=payment_method,
            SavedPaymentMethod=saved_method,
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
        cart_obj = Cart.objects.filter(Customer=customer).first()
        if cart_obj:
            CartItem.objects.filter(Cart=cart_obj).delete()

        # Clear session
        del request.session['order_id']
        del request.session['payment_method']

        return redirect('order_success')

    # Figure out if the customer already has a saved profile for the chosen method
    existing_saved_method = None
    if payment_method:
        existing_saved_method = saved_methods.filter(PaymentMethod=payment_method).first()

    default_method = saved_methods.filter(IsDefault=True).first()

    return render(request, 'payments/payment.html', {
        'order': order,
        'payment_method': payment_method,
        'existing_saved_method': existing_saved_method,
        'default_method': default_method,
        'saved_methods': saved_methods,
        'mobile_money_methods': MOBILE_MONEY_METHODS,
        'card_methods': CARD_METHODS,
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


@login_required(login_url='/accounts/login/')
def payment_methods(request):
    """Manage saved payment methods: list, add, set default, delete."""
    customer = get_object_or_404(Customer, User=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            method = request.POST.get('payment_method')
            set_default = request.POST.get('set_default') == 'on'

            if method in MOBILE_MONEY_METHODS:
                SavedPaymentMethod.objects.create(
                    Customer=customer,
                    PaymentMethod=method,
                    PhoneNumber=request.POST.get('phone_number', '').strip(),
                    IsDefault=set_default,
                )
            elif method in CARD_METHODS:
                SavedPaymentMethod.objects.create(
                    Customer=customer,
                    PaymentMethod=method,
                    BankAccountNumber=request.POST.get('bank_account_number', '').strip(),
                    BankName=request.POST.get('bank_name', '').strip(),
                    IsDefault=set_default,
                )

        elif action == 'set_default':
            method_id = request.POST.get('method_id')
            saved_method = get_object_or_404(SavedPaymentMethod, id=method_id, Customer=customer)
            saved_method.IsDefault = True
            saved_method.save()

        elif action == 'delete':
            method_id = request.POST.get('method_id')
            SavedPaymentMethod.objects.filter(id=method_id, Customer=customer).delete()

        return redirect('payment_methods')

    saved_methods = SavedPaymentMethod.objects.filter(Customer=customer)

    return render(request, 'payments/payment_methods.html', {
        'saved_methods': saved_methods,
        'mobile_money_methods': MOBILE_MONEY_METHODS,
        'card_methods': CARD_METHODS,
        'brands': get_brands(),
    })