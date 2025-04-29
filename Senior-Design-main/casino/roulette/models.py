from django.db import models


class User(models.Model):
    userid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    username = models.CharField(max_length=255)  # Username field
    password = models.CharField(max_length=255)  # Password field


    def str(self):
        return self.username

class Roulette(models.Model):
    spinid = models.AutoField(primary_key=True)  # Auto-incrementing primary key
    number = models.IntegerField()  # Spin number field
    color = models.CharField(max_length=10)     # Color of the spin result (e.g., 'red', 'black', 'green')

    def str(self):
        return f"Spin ID: {self.spinid}, Number: {self.number}, Color: {self.color}"
    class Meta:
        db_table = 'roulette'  # Explicitly set the table name


class UserBets(models.Model):
    userid = models.IntegerField()
    betid = models.AutoField(primary_key = True)  # Adjust the field type as needed
    betamount = models.DecimalField(max_digits=10, decimal_places=2)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    chipcount = models.IntegerField(default=0)
    class Meta:
        db_table = 'userbets'
    def str(self):
        return f"User {self.userid} - Bet {self.betid} - Amount {self.betamount}"
