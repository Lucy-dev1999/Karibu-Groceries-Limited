from django.urls import path
from . import views

urlpatterns = [

    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Stock
    path('stock/', views.all_stock, name='all_stock'),
    path('stock/add/', views.add_stock, name='add_stock'),

    # Sales
    path('sales/add/', views.add_sale, name='add_sale'),
    path('sales/', views.all_sales, name='all_sales'),

    # Credits
    path('credits/add/<int:sale_id>/', views.add_credit, name='add_credit'),
    path('credits/', views.all_credits, name='all_credits'),

    # Sale Details & Receipt
    path('sale/<int:sale_id>/', views.view_sale, name='view_sale'),
    path('receipt/<int:sale_id>/', views.receipt, name='receipt'),
]