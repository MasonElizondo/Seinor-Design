from django.contrib import admin
from django.urls import path, include
from roulette import views  # Import the index view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.index, name='login'),  # Redirect to login
    path('', views.index, name='index'),  # Home page
    path('roulette/', include('roulette.urls')),  # Include roulette app URLs


]
