from django.shortcuts import render, get_object_or_404
from .models import Product, Brand
from django.db.models import Sum, Count

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