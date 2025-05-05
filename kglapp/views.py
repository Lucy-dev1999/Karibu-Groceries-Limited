from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from .forms import LoginForm, StockForm, SaleForm, CreditForm
from .models import Stock, Sale, Credit
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from functools import wraps

def has_role(roles):
    def check_role(user):
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if isinstance(roles, str):
            return user.role == roles
        return user.role in roles
    return user_passes_test(check_role)

def branch_access_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or request.user.role == 'director':
            return view_func(request, *args, **kwargs)
            
        # Get the branch parameter from URL or object
        branch = request.GET.get('branch')
            
        # If no branch specified in URL, check objects
        if not branch:
            if 'stock_id' in kwargs:
                obj = Stock.objects.get(id=kwargs['stock_id'])
                branch = obj.branch
            elif 'sale_id' in kwargs:
                obj = Sale.objects.get(id=kwargs['sale_id'])
                branch = obj.branch
            elif 'credit_id' in kwargs:
                obj = Credit.objects.get(id=kwargs['credit_id'])
                branch = obj.branch
            
        # If still no branch found, default to user's branch
        if not branch:
            branch = request.user.branch

        # Check if user has access to the branch
        if request.user.role == 'sales_agent':
            if branch != request.user.branch:
                raise PermissionDenied("You don't have permission to access this branch's data.")
        elif branch != request.user.branch:
            raise PermissionDenied("You don't have permission to access this branch's data.")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# --- Login View ---
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'login.html', {
        'form': form,
    })

# --- Dashboard View ---
@login_required
def dashboard(request):
    branch = request.GET.get('branch')
    
    if request.user.role == 'sales_agent':
        # Get recent sales count (last 7 days)
        from django.utils import timezone
        from datetime import timedelta
        seven_days_ago = timezone.now().date() - timedelta(days=7)
        
        recent_sales_count = Sale.objects.filter(
            sales_agent=request.user,
            date_of_sale__gte=seven_days_ago
        ).count()
        
        # Get active credits count
        active_credits_count = Credit.objects.filter(
            sales_agent=request.user,
            branch=request.user.branch
        ).count()
        
        # Get recent activities (sales and credits)
        sales = Sale.objects.filter(
            sales_agent=request.user
        ).order_by('-date_of_sale')[:5]
        
        credits = Credit.objects.filter(
            sales_agent=request.user
        ).order_by('-dispatch_date')[:5]
        
        # Combine and sort activities
        recent_activities = []
        for sale in sales:
            recent_activities.append({
                'id': sale.id,
                'date': sale.date_of_sale,
                'type': 'sale',
                'details': f"{sale.name_of_produce} - {sale.tonnage}kg to {sale.buyers_name}"
            })
        
        for credit in credits:
            recent_activities.append({
                'id': credit.id,
                'date': credit.dispatch_date,
                'type': 'credit',
                'details': f"{credit.produce_name} - {credit.tonnage}kg to {credit.buyers_name}"
            })
        
        # Sort by date descending
        recent_activities.sort(key=lambda x: x['date'], reverse=True)
        recent_activities = recent_activities[:10]  # Keep only 10 most recent

        template = 'sales_agent_dashboard.html'
        context = {
            'recent_sales_count': recent_sales_count,
            'active_credits_count': active_credits_count,
            'recent_activities': recent_activities,
            'user_branch': request.user.branch,
            'user': request.user
        }
    elif request.user.role == 'manager':
        # Get branch stats
        branch_stats = Stock.get_total_stock_by_branch(request.user.branch)
        # Get per-item statistics
        stock_by_item = Stock.get_stock_by_item(request.user.branch)
        sales_by_item = Sale.get_sales_by_item(request.user.branch)
        credits_by_item = Credit.get_credits_by_item(request.user.branch)
        
        # Combine all unique items
        all_items = set(list(stock_by_item.keys()) + 
                       list(sales_by_item.keys()) + 
                       list(credits_by_item.keys()))
        
        # Create item statistics
        item_stats = []
        for item in all_items:
            item_stats.append({
                'name': item,
                'current_stock': stock_by_item.get(item, 0),
                'total_sales': sales_by_item.get(item, 0),
                'total_credits': credits_by_item.get(item, 0)
            })
        
        template = 'dashboard.html'
        context = {
            'branch_stats': branch_stats,
            'user_branch': request.user.branch,
            'user_role': request.user.role,
            'current_branch': request.user.branch,
            'item_stats': item_stats
        }
    
    elif request.user.role == 'director':
        # Get branch parameter
        branch = request.GET.get('branch')

        # Calculate statistics for each branch
        mattuga_stats = {
            'stock': Stock.get_total_stock_by_branch('Mattuga'),
            'sales': sum(float(sale.tonnage) for sale in Sale.objects.filter(branch='Mattuga')),
            'credits': sum(float(credit.tonnage) for credit in Credit.objects.filter(branch='Mattuga')),
            'stock_items': Stock.get_stock_by_item('Mattuga'),
            'sales_items': Sale.get_sales_by_item('Mattuga'),
            'credits_items': Credit.get_credits_by_item('Mattuga')
        }
        
        maganjo_stats = {
            'stock': Stock.get_total_stock_by_branch('Maganjo'),
            'sales': sum(float(sale.tonnage) for sale in Sale.objects.filter(branch='Maganjo')),
            'credits': sum(float(credit.tonnage) for credit in Credit.objects.filter(branch='Maganjo')),
            'stock_items': Stock.get_stock_by_item('Maganjo'),
            'sales_items': Sale.get_sales_by_item('Maganjo'),
            'credits_items': Credit.get_credits_by_item('Maganjo')
        }

        # Calculate combined totals
        stats = {
            'Mattuga': mattuga_stats,
            'Maganjo': maganjo_stats,
            'total_stock': mattuga_stats['stock'] + maganjo_stats['stock'],
            'total_sales': mattuga_stats['sales'] + maganjo_stats['sales'],
            'total_credits': mattuga_stats['credits'] + maganjo_stats['credits']
        }

        template = 'director_dashboard.html'
        context = {
            'branch_stats': stats,
            'branches': ['Mattuga', 'Maganjo'],
            'current_branch': branch,
            'user_branch': branch or request.user.branch,
            'user': request.user,
        }
    
    return render(request, template, context)

# --- Stock Management Views ---
@login_required
@has_role(['manager', 'director'])
def add_stock(request):
    branch = request.GET.get('branch')
    if request.method == 'POST':
        form = StockForm(request.POST, user=request.user, branch=branch)
        if form.is_valid():
            try:
                stock = form.save(commit=False)
                if request.user.role == 'director':
                    stock.branch = branch or request.user.branch
                else:
                    stock.branch = request.user.branch
                stock.save()
                messages.success(request, f'Successfully added {stock.tonnage}kg of {stock.name_of_produce} to stock.')
                return redirect('all_stock')
            except Exception as e:
                messages.error(request, f'Error saving stock: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}')
    else:
        form = StockForm(user=request.user, branch=branch)
        
    return render(request, 'add_stock.html', {
        'form': form,
        'user_branch': branch or request.user.branch,
    })

@login_required
@has_role(['manager', 'director'])
def edit_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    # Check branch access for managers
    if request.user.role == 'manager' and stock.branch != request.user.branch:
        raise PermissionDenied("You don't have permission to edit this stock item.")
        
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('all_stock')
    else:
        form = StockForm(instance=stock, user=request.user)
    return render(request, 'add_stock.html', {'form': form, 'edit_mode': True})

@login_required
@has_role(['manager', 'director'])
def delete_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    # Check branch access for managers
    if request.user.role == 'manager' and stock.branch != request.user.branch:
        raise PermissionDenied("You don't have permission to delete this stock item.")
    stock.delete()
    return redirect('all_stock')

# --- All Stock ---
@login_required
@has_role(['manager', 'director'])
def all_stock(request):
    branch = request.GET.get('branch')
    if request.user.role == 'manager':
        # For managers, ensure they can only see their assigned branch
        stocks = Stock.objects.filter(branch=request.user.branch)
        branch = request.user.branch
    elif request.user.role == 'director':
        # Directors can see all stock or filter by branch
        if branch in ['Mattuga', 'Maganjo']:
            stocks = Stock.objects.filter(branch=branch)
        else:
            stocks = Stock.objects.all()
    return render(request, 'all_stock.html', {'stocks': stocks, 'current_branch': branch})

@login_required
@has_role(['manager', 'director'])
@branch_access_required
def view_stock(request, stock_id):
    stock = get_object_or_404(Stock, id=stock_id)
    return render(request, 'view_stock.html', {'stock': stock})

# --- Sale Management Views ---
@login_required
@has_role(['manager', 'sales_agent', 'director'])
def add_sale(request):
    branch = request.GET.get('branch')
    if request.method == 'POST':
        form = SaleForm(request.POST, user=request.user, branch=branch)
        if form.is_valid():
            sale = form.save(commit=False)
            if request.user.role == 'sales_agent':
                sale.sales_agent = request.user
                sale.branch = request.user.branch
            elif request.user.role == 'manager':
                sale.branch = request.user.branch
            elif request.user.role == 'director':
                sale.branch = branch or request.user.branch
            try:
                stock = Stock.objects.get(name_of_produce=sale.name_of_produce, branch=sale.branch)
                if stock.tonnage >= sale.tonnage:
                    stock.tonnage -= sale.tonnage
                    stock.save()
                    sale.save()
                    return redirect('all_sales')
                else:
                    form.add_error('tonnage', 'Not enough stock available.')
            except Stock.DoesNotExist:
                form.add_error('name_of_produce', 'Stock item not found in this branch.')
    else:
        form = SaleForm(user=request.user, branch=branch)
    return render(request, 'add_sale.html', {
        'form': form,
        'branch': branch or request.user.branch
    })

@login_required
@has_role(['manager'])
def delete_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    # Add stock back to inventory
    try:
        stock = Stock.objects.get(
            name_of_produce=sale.name_of_produce,
            branch=sale.branch  # Add branch filter to get the correct stock item
        )
        stock.tonnage += sale.tonnage
        stock.save()
    except Stock.DoesNotExist:
        pass
    sale.delete()
    return redirect('all_sales')

@login_required
@has_role(['manager', 'sales_agent', 'director'])
def all_sales(request):
    branch = request.GET.get('branch')
    sort_by = request.GET.get('sort', '-date_of_sale')  # Default sort by date descending
    
    if request.user.role == 'manager':
        # Managers can only see their branch's sales
        sales = Sale.objects.filter(branch=request.user.branch)
        branch = request.user.branch
    elif request.user.role == 'sales_agent':
        # Sales agents can only see sales from their branch
        sales = Sale.objects.filter(branch=request.user.branch)
        branch = request.user.branch
    else:
        # Directors can see all sales or filter by branch
        if branch in ['Mattuga', 'Maganjo']:
            sales = Sale.objects.filter(branch=branch)
        else:
            sales = Sale.objects.all()
    
    # Apply sorting
    if sort_by.startswith('-'):
        sort_field = sort_by[1:]
        is_ascending = False
    else:
        sort_field = sort_by
        is_ascending = True
    
    valid_sort_fields = ['date_of_sale', 'name_of_produce', 'tonnage']
    if sort_field in valid_sort_fields:
        sales = sales.order_by(sort_by)
    
    return render(request, 'all_sales.html', {
        'sales': sales, 
        'current_branch': branch,
        'sort_by': sort_by,
        'is_ascending': is_ascending
    })

@login_required
@has_role(['manager', 'sales_agent', 'director'])
@branch_access_required
def view_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'view_sale.html', {'sale': sale})

# --- Credit Management Views ---
@login_required
@has_role(['manager', 'sales_agent', 'director'])
def add_credit(request):
    branch = request.GET.get('branch')
    if request.method == 'POST':
        form = CreditForm(request.POST, user=request.user, branch=branch)
        if form.is_valid():
            credit = form.save(commit=False)
            if request.user.role == 'sales_agent':
                credit.sales_agent = request.user
                credit.branch = request.user.branch
            elif request.user.role == 'manager':
                credit.branch = request.user.branch
            elif request.user.role == 'director':
                credit.branch = branch or request.user.branch
            credit.save()
            return redirect('all_credits')
    else:
        form = CreditForm(user=request.user, branch=branch)
    return render(request, 'add_credit.html', {
        'form': form,
        'branch': branch or request.user.branch
    })

@login_required
@has_role(['manager', 'sales_agent'])
def add_credit_from_sale(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    if request.method == 'POST':
        form = CreditForm(request.POST, user=request.user)
        if form.is_valid():
            credit = form.save(commit=False)
            if request.user.role == 'sales_agent':
                credit.sales_agent = request.user
                credit.branch = request.user.branch
            elif request.user.role == 'manager':
                credit.branch = request.user.branch
            credit.save()
            return redirect('all_credits')
    else:
        initial_data = {
            'buyers_name': sale.buyers_name,
            'amount_due': sale.amount_paid,
            'sales_agent': sale.sales_agent,
            'produce_name': sale.name_of_produce,
            'tonnage': sale.tonnage,
            'branch': sale.branch
        }
        form = CreditForm(initial=initial_data, user=request.user)
    return render(request, 'add_credit.html', {'form': form, 'sale': sale})

@login_required
@has_role(['manager', 'sales_agent', 'director'])
def edit_credit(request, credit_id):
    credit = get_object_or_404(Credit, id=credit_id)
    # Check branch access
    if request.user.role == 'sales_agent' and credit.branch != request.user.branch:
        raise PermissionDenied("You don't have permission to edit this credit.")
        
    if request.method == 'POST':
        form = CreditForm(request.POST, instance=credit, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('all_credits')
    else:
        form = CreditForm(instance=credit, user=request.user)
    return render(request, 'add_credit.html', {'form': form, 'edit_mode': True})

@login_required
@has_role(['manager', 'sales_agent', 'director'])
def delete_credit(request, credit_id):
    credit = get_object_or_404(Credit, id=credit_id)
    # Check branch access
    if request.user.role == 'sales_agent' and credit.branch != request.user.branch:
        raise PermissionDenied("You don't have permission to delete this credit.")
    credit.delete()
    return redirect('all_credits')

@login_required
@has_role(['manager', 'sales_agent', 'director'])
def all_credits(request):
    branch = request.GET.get('branch')
    if request.user.role == 'manager':
        # Managers can only see their branch's credits
        credits = Credit.objects.filter(branch=request.user.branch)
        branch = request.user.branch
    elif request.user.role == 'sales_agent':
        # Sales agents can only see credits from their branch
        credits = Credit.objects.filter(branch=request.user.branch)
        branch = request.user.branch
    else:
        # Directors can see all credits or filter by branch
        if branch in ['Mattuga', 'Maganjo']:
            credits = Credit.objects.filter(branch=branch)
        else:
            credits = Credit.objects.all()
    return render(request, 'all_credits.html', {'credits': credits, 'current_branch': branch})

@login_required
@has_role(['manager', 'sales_agent', 'director'])
@branch_access_required
def view_credit(request, credit_id):
    credit = get_object_or_404(Credit, id=credit_id)
    return render(request, 'view_credit.html', {'credit': credit})

# --- Receipt ---
@login_required
@has_role(['manager', 'sales_agent', 'director'])
@branch_access_required
def receipt(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    return render(request, 'receipt.html', {'sale': sale})

