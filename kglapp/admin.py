from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from .models import Stock, Sale, Credit

admin.site.register(Stock)
admin.site.register(Sale)
admin.site.register(Credit)
