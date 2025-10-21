from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import Product, Comment


# 🏠 Home / Search Page
def index(request):
    query = request.GET.get('q') or request.GET.get('search')
    products = Product.objects.filter(name__icontains=query) if query else Product.objects.all()
    return render(request, 'index.html', {'products': products, 'query': query})


# 🔑 Login Page
def login_page(request):
    if request.method == 'POST':
        return redirect('products:product-list')
    return render(request, 'login.html')


# 📝 Register Page
def register_page(request):
    if request.method == 'POST':
        return redirect('products:login')
    return render(request, 'register.html')


# ➕ Add to Cart (Success Message)
def add_to_cart(request, item_id):
    product = get_object_or_404(Product, id=item_id)
    cart = request.session.get('cart', {})

    product_id = str(product.id)
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart

    cart_url = reverse('products:view-cart')
    messages.success(
        request,
        f"🛒 {product.name} added to your cart! "
        f"<a href='{cart_url}' class='btn btn-sm btn-outline-light ms-2'>Check Cart Now</a>",
        extra_tags='safe'
    )
    return redirect('products:product-list')


# 🛒 View Cart Page
def view_cart(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        product.quantity = quantity
        product.total_price = product.price * quantity
        products.append(product)
        total += product.total_price

    context = {
        'products': products,
        'total': total,
        'query': request.GET.get('q', ''),
    }
    return render(request, 'cart.html', context)


# ❌ Delete Item from Cart
def delete_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.info(request, "🗑️ Item removed from your cart successfully.")
    else:
        messages.warning(request, "Item not found in your cart.")

    return redirect('products:view-cart')


# 💳 Checkout Page
def checkout(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        product.quantity = quantity
        product.total_price = product.price * quantity
        products.append(product)
        total += product.total_price

    total_kobo = int(total * 100)

    context = {
        'products': products,
        'total': total,
        'total_kobo': total_kobo,
        'paystack_public_key': 'pk_test_your_public_key_here',
        'query': request.GET.get('q', ''),
    }
    return render(request, 'checkout.html', context)


# ✅ Confirm Payment
def confirm_payment(request):
    if request.method == 'POST':
        messages.success(request, "✅ Payment confirmed! Thank you for shopping with RedCart.")
        request.session['cart'] = {}
        return redirect('products:product-list')
    return redirect('products:checkout')


# 📦 Product Detail Page + Comments
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    additional_images = getattr(product, 'additional_images', [])
    comments = product.comments.all().order_by('-created_at') if hasattr(product, 'comments') else []

    if request.method == 'POST':
        name = request.POST.get('name')
        text = request.POST.get('text')
        rating = request.POST.get('rating')
        if name and text and rating:
            Comment.objects.create(product=product, name=name, text=text, rating=rating)
            messages.success(request, "💬 Thank you for your review!")
            return redirect('products:product-detail', product_id=product.id)

    return render(request, 'product_detail.html', {
        'product': product,
        'comments': comments,
        'additional_images': additional_images,
        'query': request.GET.get('q', ''),
    })


# ⚡ Buy Now (Direct Checkout)
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    request.session['cart'] = {str(product.id): 1}
    return redirect('products:checkout')
