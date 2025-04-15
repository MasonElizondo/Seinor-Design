from django.db import models

class User(models.Model):
    userid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    username = models.CharField(max_length=255)  # Username field
    password = models.CharField(max_length=255)  # Password field
    chipcount = models.IntegerField(default=1000)  # Chip count with a default value

    def __str__(self):
        return self.username


class Roulette(models.Model):
    spinid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    number = models.IntegerField()  # Spin number field
    color = models.CharField(max_length=10)  # Color field

    def __str__(self):
        return f"Spin {self.spinid}: {self.number} ({self.color})"


class UserBet(models.Model):
    betid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    userid = models.IntegerField()  # User ID
    betamount = models.IntegerField(null=True, blank=True)  # Bet amount (optional)
    earnings = models.IntegerField(null=True, blank=True)  # Earnings (optional)

    def __str__(self):
        return f"Bet {self.betid} with earnings: {self.earnings}"
