from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('', views.index, name='home'),  # Redirect to the home page
    path('roulette/', views.roulette, name='roulette'),  # Define the 'roulette' URL pattern
]
