from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('', views.index, name='home'),
    path('roulette/', views.roulette, name='roulette'),
    path('createAccount/', views.create_account, name='createAccount'),  # Define the 'createAccount' URL pattern
]

