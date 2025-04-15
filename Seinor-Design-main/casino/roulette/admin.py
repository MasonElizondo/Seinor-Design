from django.contrib import admin
from .models import User, Roulette, UserBet

# Register your models here
admin.site.register(User)
admin.site.register(Roulette)
admin.site.register(UserBet)
