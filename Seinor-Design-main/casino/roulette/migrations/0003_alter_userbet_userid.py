# Generated by Django 5.1.3 on 2025-04-15 01:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roulette', '0002_roulette_userbet_remove_bet_user_delete_roulettespin_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userbet',
            name='userid',
            field=models.IntegerField(),
        ),
    ]
