from django.shortcuts import render, get_object_or_404
from .models import Product, Brand
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from orders.models import CartItem

def home(request):
    brands = Brand.objects.all()
    products = Product.objects.all()

    # Filter by brand
    brand_id = request.GET.get('brand')
    if brand_id:
        products = products.filter(Brand__id=brand_id)

    # Search
    query = request.GET.get('q')
    if query:
        products = products.filter(ProductName__icontains=query)

    return render(request, 'products/home.html', {
        'products': products,
        'brands': brands,
    })


def product_detail(request, product_id):
    brands = Brand.objects.all()
    product = get_object_or_404(Product, id=product_id)

    return render(request, 'products/product_detail.html', {
        'product': product,
        'brands': brands,
    })
    @staff_member_required

 reports(request):
    from orders.models import Order
    from payments.models import Payment

    total_sales = Payment.objects.filter(
        PaymentStatus='Completed'
    ).aggregate(total=Sum('Amount'))['total'] or 0

    total_orders = Order.objects.count()

    best_sellers = CartItem.objects.values(
        'Product__ProductName'
    ).annotate(
        total_sold=Sum('Quantity')
    ).order_by('-total_sold')[:5]

    monthly_orders = Order.objects.extra(
        select={'month': "strftime('%Y-%m', OrderDate)"}
    ).values('month').annotate(
        count=Count('id')
    ).order_by('-month')[:6]

    return render(request, 'products/reports.html', {
        'total_sales': total_sales,
        'total_orders': total_orders,
        'best_sellers': best_sellers,
        'monthly_orders': monthly_orders,
        'brands': Brand.objects.all(),
    })