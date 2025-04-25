from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Stock, Sale, Credit

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['name', 'quantity', 'price', 'expiry_date', 'storage_condition']

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['name_of_produce', 'tonnage', 'amount_paid', 'buyers_name', 
                 'sales_agent_name', 'time_of_sale']

class CreditForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = ['buyers_name', 'national_id', 'location', 'contacts', 
                 'amount_due', 'sales_agent_name', 'due_date', 'produce_name', 
                 'produce_type', 'tonnage']
