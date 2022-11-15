from django.urls import path
from . import views

urlpatterns = [
	path('login', views.handleLogin),
	path('logout', views.handleLogout)
]