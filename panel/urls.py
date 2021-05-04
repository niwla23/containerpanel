from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('containers/<str:container_id>/', views.container, name="container"),
    path('containers/<str:container_id>/stop', views.power_action, name="power_action")
]
