"""
URL configuration for kgl project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from kglapp import views

urlpatterns = [
    path('admin/login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='admin_login'),
    path('admin/', admin.site.urls),
    
    # Authentication
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    # Stock
    path('stock/', views.all_stock, name='all_stock'),
    path('stock/add/', views.add_stock, name='add_stock'),
    path('stock/<int:stock_id>/', views.view_stock, name='view_stock'),
    path('stock/edit/<int:stock_id>/', views.edit_stock, name='edit_stock'),
    path('stock/delete/<int:stock_id>/', views.delete_stock, name='delete_stock'),

    # Sales
    path('sales/add/', views.add_sale, name='add_sale'),
    path('sales/', views.all_sales, name='all_sales'),
    path('sale/<int:sale_id>/', views.view_sale, name='view_sale'),
    path('sale/delete/<int:sale_id>/', views.delete_sale, name='delete_sale'),

    # Credits
    path('credits/add/', views.add_credit, name='add_credit'),
    path('credits/add/<int:sale_id>/', views.add_credit_from_sale, name='add_credit_from_sale'),
    path('credits/', views.all_credits, name='all_credits'),
    path('credit/<int:credit_id>/', views.view_credit, name='view_credit'),
    path('credit/edit/<int:credit_id>/', views.edit_credit, name='edit_credit'),
    path('credit/delete/<int:credit_id>/', views.delete_credit, name='delete_credit'),

    # Receipt
    path('receipt/<int:sale_id>/', views.receipt, name='receipt'),
]
