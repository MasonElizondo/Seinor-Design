from django.contrib import admin
from .models import User, Roulette, UserBets

# Register your models here
admin.site.register(Roulette)
admin.site.register(UserBets)

