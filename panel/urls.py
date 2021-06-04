from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add/choose', views.add_choose, name="add_choose"),
    path('add/choose_template', views.choose_template, name="choose_template"),
    path('add/template/<str:template_name>', views.template_add, name="template_add"),
    path('add/new', views.add_new, name="add_new"),
    path('login', views.login, name='login'),
    path('containers/<str:container_id>/', views.container, name="container"),
    path('containers/<str:container_id>/stop', views.power_action, name="power_action")
]
