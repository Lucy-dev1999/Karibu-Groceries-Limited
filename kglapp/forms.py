from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Stock, Sale, Credit, UserProfile

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ['name_of_produce', 'type_of_produce', 'tonnage', 'name_of_dealer', 
                 'cost', 'contact', 'sell_price']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        branch = kwargs.pop('branch', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.role == 'manager':
                self.instance.branch = user.branch
            elif user.role == 'director':
                if branch:
                    self.instance.branch = branch
                self.fields['branch'] = forms.ChoiceField(
                    choices=[('Mattuga', 'Mattuga'), ('Maganjo', 'Maganjo')],
                    initial=branch or 'Mattuga'
                )
            
    def save(self, commit=True):
        instance = super().save(commit=False)
        if hasattr(self, 'cleaned_data') and 'branch' in self.cleaned_data:
            instance.branch = self.cleaned_data['branch']
        if commit:
            instance.save()
        return instance

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['name_of_produce', 'branch', 'tonnage', 'amount_paid', 'buyers_name', 
                 'sales_agent']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        branch = kwargs.pop('branch', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.role == 'manager':
                # Manager can only select sales agents from their branch
                self.fields['sales_agent'].queryset = UserProfile.objects.filter(
                    role='sales_agent', 
                    branch=user.branch
                )
                self.fields['branch'].initial = user.branch
                self.fields['branch'].widget = forms.HiddenInput()
                self.fields['branch'].disabled = True
            elif user.role == 'sales_agent':
                self.fields['sales_agent'].initial = user
                self.fields['sales_agent'].widget = forms.HiddenInput()
                self.fields['sales_agent'].disabled = True
                self.fields['branch'].initial = user.branch
                self.fields['branch'].widget = forms.HiddenInput()
                self.fields['branch'].disabled = True
            elif user.role == 'director':
                # Directors can select any branch and any sales agent
                if branch:
                    self.fields['branch'].initial = branch
                    self.fields['sales_agent'].queryset = UserProfile.objects.filter(
                        role='sales_agent',
                        branch=branch
                    )
                else:
                    self.fields['sales_agent'].queryset = UserProfile.objects.filter(
                        role='sales_agent'
                    )

class CreditForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = ['buyers_name', 'branch', 'national_id', 'location', 'contacts', 
                 'amount_due', 'sales_agent', 'due_date', 'produce_name', 
                 'produce_type', 'tonnage']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        branch = kwargs.pop('branch', None)
        super().__init__(*args, **kwargs)
        
        if user:
            if user.role == 'manager':
                # Manager can only select sales agents from their branch
                self.fields['sales_agent'].queryset = UserProfile.objects.filter(
                    role='sales_agent', 
                    branch=user.branch
                )
                self.fields['branch'].initial = user.branch
                self.fields['branch'].widget = forms.HiddenInput()
                self.fields['branch'].disabled = True
            elif user.role == 'sales_agent':
                self.fields['sales_agent'].initial = user
                self.fields['sales_agent'].widget = forms.HiddenInput()
                self.fields['sales_agent'].disabled = True
                self.fields['branch'].initial = user.branch
                self.fields['branch'].widget = forms.HiddenInput()
                self.fields['branch'].disabled = True
            elif user.role == 'director':
                # Directors can select any branch and any sales agent
                if branch:
                    self.fields['branch'].initial = branch
                    self.fields['sales_agent'].queryset = UserProfile.objects.filter(
                        role='sales_agent',
                        branch=branch
                    )
                else:
                    self.fields['sales_agent'].queryset = UserProfile.objects.filter(
                        role='sales_agent'
                    )
