from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import LoginForm, StockForm, SaleForm, CreditForm
from .models import Stock, Sale, Credit
from functools import wraps

def login_iew(request):
    """Handle user login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_owner==True:
            form = login(request, user)
            return redirect('/dashboard3')
        if  user is not None and user.is_manager==True:
            form = login(request, user)
            return redirect('/dashboard1')
        else: 
             print("something went wrong")


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if not request.user.groups.filter(name__in=roles).exists():
                return HttpResponse('Permission Denied - You do not have the required role to access this page.', status=403)
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# --- Login View ---
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# --- Dashboard View ---
@login_required
@role_required('manager', 'director')
def dashboard(request):
    return render(request, 'dashboard.html')

# --- Add Stock ---
@login_required
@role_required('manager')
def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('all_stock')
    else:
        form = StockForm()
    return render(request, 'add_stock.html', {'form': form})

# --- All Stock ---
@login_required
@role_required('manager', 'director')
def all_stock(request):
    stocks = Stock.objects.all()
    return render(request, 'all_stock.html', {'stocks': stocks})

# --- Add Sale ---
@login_required
@role_required('manager', 'sales_agent')
def add_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            sale.sold_by = request.user
            stock = sale.stock_item
            if stock.quantity >= sale.quantity_sold:
                stock.quantity -= sale.quantity_sold
                stock.save()
                sale.total_price = sale.quantity_sold * stock.price
                sale.save()

                if sale.is_credit:
                    return redirect('add_credit', sale_id=sale.id)
                return redirect('all_sales')
            else:
                form.add_error('quantity_sold', 'Not enough stock available.')
    else:
        form = SaleForm()
    return render(request, 'add_sale.html', {'form': form})

# --- Add Credit --
@login_required
@role_required('manager', 'sales_agent')
def add_credit(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            credit = form.save(commit=False)
            credit.sale = sale
            credit.save()
            return redirect('all_credits')
    else:
        form = CreditForm()
    return render(request, 'add_credit.html', {'form': form, 'sale': sale})

# --- All Credits ---
@login_required
@role_required('manager', 'director')
def all_credits(request):
    credits = Credit.objects.all()
    return render(request, 'all_credits.html', {'credits': credits})

# --- All Sales ---
@login_required
@role_required('manager', 'director')
def all_sales(request):
    sales = Sale.objects.all()
    return render(request, 'all_sales.html', {'sales': sales})

# --- View Sale ---
@login_required
@role_required('manager', 'director')
def view_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'view_sale.html', {'sale': sale})

# --- Receipt ---
@login_required
@role_required('manager')
def receipt(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'receipt.html', {'sale': sale})

