import django
from django.contrib.auth.models import User
from store.models import Address, Cart, Category, Order, Product
from django.shortcuts import redirect, render, get_object_or_404
from .forms import RegistrationForm, AddressForm
from django.contrib import messages
from django.views import View
import decimal
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
from django.core.paginator import Paginator
from .forms import ReviewForm
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Review
import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise import accuracy
import joblib, random


# This function handles the homepage of the store, displaying featured categories and products.
def home(request):
    categories = Category.objects.filter(is_active=True, is_featured=True)[:3]
    products = Product.objects.filter(is_active=True, is_featured=True)[:4]
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'store/index.html', context)


# This function displays the details of a specific product, allows users to submit reviews,
# and provides recommendations based on user reviews.
def detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)[:4]
    form = ReviewForm(request.POST)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user 
            review.save()
            # return redirect('detail', slug=slug)
    else:
        form = ReviewForm()

    review= Review.objects.filter(product=product).order_by('-rating')
    objects = Review.objects.all()
    user_id=request.user.id
    dataset = []
    model = joblib.load('store/recommendation_model.pkl')
    for review in objects:
        dataset.append({
            'UserID': review.user.id,
            'ProductID': review.product.id,
            'Rating': review.rating,
        })
    ratings_data = pd.DataFrame(dataset)
    reader = Reader(rating_scale=(0, 1))

    data = Dataset.load_from_df(ratings_data[['UserID','ProductID','Rating']], reader)

    trainset, testset = train_test_split(data, test_size=0.01)
    top_n=5

    testset = trainset.build_anti_testset()
    testset = filter(lambda x: x[0] == user_id, testset)

    predictions = model.test(testset)

    predictions.sort(key=lambda x: x.est, reverse=True)
    
    top_n_recommendations = predictions    
    recommended_product_ids = [prediction.iid for prediction in predictions]
    final=random.sample(recommended_product_ids, 4)
    recproduct=Product.objects.filter(id__in=final)
    
    print(random.sample(recommended_product_ids, 4))

    context = {
        'product': product,
        'related_products': related_products,
        'form':form,
        'recproduct':recproduct,
    }
    print(user_id)
    return render(request, 'store/detail.html', context)

# This function displays all the categories available in the store.
def all_categories(request):
    categories = Category.objects.filter(is_active=True)
    return render(request, 'store/categories.html', {'categories':categories})

# This function displays products belonging to a specific category and paginates the results.
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    paginator = Paginator(products,6)
    page_number = request.GET.get('page')
    products_final = paginator.get_page(page_number)
    categories = Category.objects.filter(is_active=True)
    context = {
        'category': category,
        'products': products_final,
        'categories': categories,
    }
    return render(request, 'store/category_products.html', context)

# This function allows users to add or edit a review for a specific product.
def add_review(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.exclude(id=product.id).filter(is_active=True, category=product.category)[:4]
    msg = ''
    existing_review = Review.objects.filter(product=product, user=request.user).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            msg = 'Review Submitted Successfully'
            # return redirect('store:', slug=slug)

        else:
            print(form.errors)

            msg = 'Review form has errors'
    else:
        form = ReviewForm(instance=existing_review)
    
    review= Review.objects.filter(product=product).order_by('-rating')
    objects = Review.objects.all()
    user_id=request.user.id
    dataset = []
    model = joblib.load('store/recommendation_model.pkl')
    for review in objects:
        dataset.append({
            'UserID': review.user.id,
            'ProductID': review.product.id,
            'Rating': review.rating,
        })
    ratings_data = pd.DataFrame(dataset)
    reader = Reader(rating_scale=(0, 1))

    data = Dataset.load_from_df(ratings_data[['UserID','ProductID','Rating']], reader)

    trainset, testset = train_test_split(data, test_size=0.01)
    top_n=5

    testset = trainset.build_anti_testset()
    testset = filter(lambda x: x[0] == user_id, testset)

    predictions = model.test(testset)

    predictions.sort(key=lambda x: x.est, reverse=True)
    
    top_n_recommendations = predictions    
    recommended_product_ids = [prediction.iid for prediction in predictions]
    final=random.sample(recommended_product_ids, 4)
    recproduct=Product.objects.filter(id__in=final)

    reviews = Review.objects.filter(product=product).order_by('-rating')

    return render(request, 'store/detail.html', {'form': form, 'product': product, 'msg': msg, 'related_products': related_products, 'reviews': reviews,'recproduct':recproduct})

# Authentication Starts Here
# This class-based view handles user registration. It displays the registration form and processes
# user registration when a POST request is received.
class RegistrationView(View):
    def get(self, request):
        form = RegistrationForm()
        return render(request, 'account/register.html', {'form': form})
    
    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Congratulations! Registration Successful!")
            form.save()
        return render(request, 'account/register.html', {'form': form})
        
# This function displays the user's profile information, including addresses and order history,
# after the user has logged in.
@login_required
def profile(request):
    addresses = Address.objects.filter(user=request.user)
    orders = Order.objects.filter(user=request.user)
    return render(request, 'account/profile.html', {'addresses':addresses, 'orders':orders})

# This class-based view handles address management. It allows users to add new addresses to their profile.
@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'account/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            reg = Address(user=user, locality=locality, city=city, state=state)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('store:profile')

# This function allows users to remove an address from their profile.
@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('store:profile')

# This function handles adding products to the user's shopping cart.
@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()
    
    return redirect('store:cart')

# This function displays the user's shopping cart, including product details, quantities, and total amount.
@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)

    # Display Total on Cart Page
    amount = decimal.Decimal(0)
    shipping_amount = decimal.Decimal(10)
    # using list comprehension to calculate total amount based on quantity and shipping
    cp = [p for p in Cart.objects.all() if p.user==user]
    if cp:
        for p in cp:
            temp_amount = (p.quantity * p.product.price)
            amount += temp_amount

    # Customer Addresses
    addresses = Address.objects.filter(user=user)

    context = {
        'cart_products': cart_products,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': amount + shipping_amount,
        'addresses': addresses,
    }
    return render(request, 'store/cart.html', context)

# This function allows users to remove a product from their shopping cart.
@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        messages.success(request, "Product removed from Cart.")
    return redirect('store:cart')

# This function allows users to increase the quantity of a product in their shopping cart.
@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('store:cart')

# This function allows users to decrease the quantity of a product in their shopping cart.
@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('store:cart')

# This function handles the checkout process, transferring items from the cart to the user's order history.
@login_required
def checkout(request):
    user = request.user
    address_id = request.GET.get('address')
    
    address = get_object_or_404(Address, id=address_id)
    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Order(user=user, address=address, product=c.product, quantity=c.quantity).save()
        # And Deleting from Cart
        c.delete()
    return redirect('store:orders')

# This function displays the user's order history.
@login_required
def orders(request):
    all_orders = Order.objects.filter(user=request.user).order_by('-ordered_date')
    return render(request, 'store/orders.html', {'orders': all_orders})

# This function handles the "Shop" page of the store.
def shop(request):
    return render(request, 'store/shop.html')

# This function is a placeholder for testing purposes.
def test(request):
    return render(request, 'store/test.html')
