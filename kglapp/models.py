from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class UserProfile(AbstractUser):
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    phone_number = models.CharField(max_length=15, null=False, blank=False)
    address = models.TextField(null=False, blank=False)
    contact = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, null=False, blank=False)
    role = models.CharField(max_length=20, choices=[
        ('manager', 'Manager'),
        ('director', 'Director'),
        ('sales_agent', 'Sales Agent')
    ], default='manager')
    branch = models.CharField(max_length=100, null=True, blank=True, choices=[
        ('Mattuga', 'Mattuga'),
        ('Maganjo', 'Maganjo'),
    ])
    date_joined = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.username
    
class Stock(models.Model):
    name_of_produce = models.CharField(max_length=100, null=False, blank=False)
    branch = models.CharField(max_length=100, null=False, blank=False, default='Mattuga', choices=[
        ('Mattuga', 'Mattuga'),
        ('Maganjo', 'Maganjo'),
    ])
    type_of_produce = models.CharField(max_length=50, null=False, blank=False)
    date_of_arrival = models.DateField(auto_now_add=True,null=False, blank=False)
    time_of_arrival = models.TimeField(auto_now_add=True,null=False, blank=False)
    tonnage = models.DecimalField(max_digits=10, decimal_places=2, null= False, blank=False)
    name_of_dealer = models.CharField(max_length=100, null=False, blank=False)
    cost = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    contact = models.CharField(max_length=20, null=False, blank=False)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)

    @classmethod
    def get_total_stock_by_branch(cls, branch):
        """Returns total tonnage of stock for a specific branch"""
        try:
            result = cls.objects.filter(branch=branch)
            total = sum(item.tonnage for item in result)
            print(f"DEBUG: {branch} branch - Found {len(result)} items, total: {total}")
            return float(total)
        except Exception as e:
            print(f"Error calculating stock for branch {branch}: {str(e)}")
            return 0.0

    @classmethod
    def get_all_branch_stats(cls):
        """Returns a dictionary with total stock for all branches"""
        try:
            mattuga_total = cls.get_total_stock_by_branch('Mattuga')
            maganjo_total = cls.get_total_stock_by_branch('Maganjo')
            print(f"DEBUG: All branch stats - Mattuga: {mattuga_total}, Maganjo: {maganjo_total}")
            return {
                'Mattuga': float(mattuga_total),
                'Maganjo': float(maganjo_total)
            }
        except Exception as e:
            print(f"Error getting all branch stats: {str(e)}")
            return {'Mattuga': 0.0, 'Maganjo': 0.0}

    @classmethod
    def get_stock_by_item(cls, branch=None):
        """Returns a dictionary of total stock for each item in a branch"""
        try:
            query = cls.objects.all()
            if branch:
                query = query.filter(branch=branch)
            
            items = {}
            for stock in query:
                if stock.name_of_produce in items:
                    items[stock.name_of_produce] += float(stock.tonnage)
                else:
                    items[stock.name_of_produce] = float(stock.tonnage)
            return items
        except Exception as e:
            print(f"Error calculating stock by item: {str(e)}")
            return {}

    def __str__(self):
        return f"{self.name_of_produce} - {self.tonnage}kg"

    def get_stock_status(self):
        if self.tonnage < 100:
            return "Low"
        elif self.tonnage < 500:
            return "Medium"
        else:
            return "Good"

class Sale(models.Model):
    name_of_produce = models.CharField(max_length=100, null=False, blank=False)
    branch = models.CharField(max_length=100, null=False, blank=False, default='Mattuga', choices=[
        ('Mattuga', 'Mattuga'),
        ('Maganjo', 'Maganjo'),
    ])
    tonnage = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)
    buyers_name = models.CharField(max_length=100)
    sales_agent = models.ForeignKey(
        'UserProfile',
        on_delete=models.PROTECT,
        limit_choices_to={'role': 'sales_agent'}
    )
    date_of_sale = models.DateField(auto_now_add=True, null=False, blank=False)
    time_of_sale = models.TimeField(auto_now_add=True, null=False, blank=False)

    @classmethod
    def get_sales_by_item(cls, branch=None):
        """Returns a dictionary of total sales for each item in a branch"""
        try:
            query = cls.objects.all()
            if branch:
                query = query.filter(branch=branch)
            
            items = {}
            for sale in query:
                if sale.name_of_produce in items:
                    items[sale.name_of_produce] += float(sale.tonnage)
                else:
                    items[sale.name_of_produce] = float(sale.tonnage)
            return items
        except Exception as e:
            print(f"Error calculating sales by item: {str(e)}")
            return {}

    def __str__(self):
        return f"{self.buyers_name} - {self.name_of_produce}"

class Credit(models.Model):
    buyers_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, null=False, blank=False, default='Mattuga', choices=[
        ('Mattuga', 'Mattuga'),
        ('Maganjo', 'Maganjo'),
    ])
    national_id = models.CharField(max_length=20, unique=True, null=False, blank=False)
    location = models.CharField(max_length=100)
    contacts = models.CharField(max_length=20)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0) 
    sales_agent = models.ForeignKey(
        'UserProfile',
        on_delete=models.PROTECT,
        limit_choices_to={'role': 'sales_agent'}
    )
    due_date = models.DateField(null=False, blank=False)
    produce_name = models.CharField(max_length=100, null=False, blank=False)
    produce_type = models.CharField(max_length=50, null=False, blank=False)
    tonnage = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    dispatch_date = models.DateField(auto_now_add=True, null=False, blank=False)

    @classmethod
    def get_credits_by_item(cls, branch=None):
        """Returns a dictionary of total credits for each item in a branch"""
        try:
            query = cls.objects.all()
            if branch:
                query = query.filter(branch=branch)
            
            items = {}
            for credit in query:
                if credit.produce_name in items:
                    items[credit.produce_name] += float(credit.tonnage)
                else:
                    items[credit.produce_name] = float(credit.tonnage)
            return items
        except Exception as e:
            print(f"Error calculating credits by item: {str(e)}")
            return {}

    def __str__(self):
        return f"{self.buyers_name} - {self.amount_due}"




