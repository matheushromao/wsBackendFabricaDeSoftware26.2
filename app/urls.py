from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("cadastro/", views.cadastro, name="cadastro"),
    path("login/", auth_views.LoginView.as_view(template_name="app/login.html"), name="login"),
    path("logout", auth_views.LogoutView.as_view(), name="logout"),
    
    path("", views.home, name="home"),
    path("time/novo/", views.criar_time, name="criar_time"),
    path("time/<int:pk>/editar/", views.editar_time, name="editar_time"),
    path("time/<int:pk>/excluir/", views.excluir_time, name="excluir_time"),
]
