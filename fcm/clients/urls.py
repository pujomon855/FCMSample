# -*- coding: utf-8 -*-

from django.urls import path

from . import views

app_name = 'clients'
urlpatterns = [
    # ex: /clients/
    path('', views.IndexView.as_view(), name='index'),
    # ex: /clients/table/
    path('table/', views.ClientTableView.as_view(), name='table'),
    # ex: /clients/3/
    path('<int:pk>/', views.show_detail, name='detail'),

    # for admin form
    path('admin/client_classifier/', views.get_trade_type, name='ajax_trade_type')
]
