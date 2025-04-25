from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class UserProfile(AbstractUser):
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    contact = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return self.username
    
class Stock(models.Model):
    name_of_produce = models.CharField(max_length=100, null=False, blank=False)
    type_of_produce = models.CharField(max_length=50, null=False, blank=False)
    date_of_arrival = models.DateField(auto_now_add=True,null=False, blank=False)
    time_of_arrival = models.TimeField(auto_now_add=True,null=False, blank=False)
    tonnage = models.DecimalField(max_digits=10, decimal_places=2)
    name_of_dealer = models.CharField(max_length=100, null=False, blank=False)
    cost = models.DecimalField(max_digits=12, decimal_places=2)
    contact = models.CharField(max_length=15)
    sell_price = models.DecimalField(max_digits=12, decimal_places=2)
    expiry_date = models.DateField(null=True, blank=True)
    storage_condition = models.CharField(max_length=100, null=True, blank=True)

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
    name_of_produce = models.CharField(max_length=100)
    tonnage = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    buyers_name = models.CharField(max_length=100)
    sales_agent_name = models.CharField(max_length=100)
    date_of_sale = models.DateField(auto_now_add=True)
    time_of_sale = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyers_name} - {self.name_of_produce}"

class Credit(models.Model):
    buyers_name = models.CharField(max_length=100)
    national_id = models.CharField(max_length=20, unique=True)
    location = models.CharField(max_length=100)
    contacts = models.CharField(max_length=15)
    amount_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Added default value
    sales_agent_name = models.CharField(max_length=100)
    due_date = models.DateField()
    produce_name = models.CharField(max_length=100)
    produce_type = models.CharField(max_length=50)
    tonnage = models.DecimalField(max_digits=10, decimal_places=2)
    dispatch_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyers_name} - {self.amount_due}"




