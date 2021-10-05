"""
This file maps URL patterns to view functions to handle them.
Graphql views are not injected here.
"""

from django.urls import path

from . import views

urlpatterns = [
    path('is_authenticated', views.is_authenticated, name='is_authenticated'),
]
