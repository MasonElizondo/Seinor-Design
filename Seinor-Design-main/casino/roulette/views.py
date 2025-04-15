from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import User, Roulette, UserBet
import random


def index(request):
    return render(request, 'index.html')  # Render the homepage

@login_required
def roulette(request):
    past_spins = Roulette.objects.all().order_by('-spinid')[:10]  # Fetch the last 10 spins
    return render(request, 'roulette/roulette.html', {
        'past_spins': past_spins,
        'balance': request.session.get('balance', 1000),
    })


RED_NUMBERS = {
    1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
}

def get_color(number):
    if number == 0:
        return 'green'
    return 'red' if number in RED_NUMBERS else 'black'

def spin_roulette():
    number = random.randint(0, 36)
    color = get_color(number)
    return number, color

def evaluate_bet(bet_type, value, amount, spin_number, spin_color):
    if bet_type == "straight" and value.isdigit() and int(value) == spin_number:
        return amount * 35
    elif bet_type == "color" and value.lower() == spin_color:
        return amount * 2
    elif bet_type == "even_odd":
        if spin_number != 0:
            if value == "even" and spin_number % 2 == 0:
                return amount * 2
            elif value == "odd" and spin_number % 2 == 1:
                return amount * 2
    elif bet_type == "dozen":
        if value == "1st" and 1 <= spin_number <= 12:
            return amount * 3
        elif value == "2nd" and 13 <= spin_number <= 24:
            return amount * 3
        elif value == "3rd" and 25 <= spin_number <= 36:
            return amount * 3
    elif bet_type == "column":
        column_map = {
            "1st": [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
            "2nd": [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
            "3rd": [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36],
        }
        if spin_number in column_map.get(value, []):
            return amount * 3
    return 0


@login_required
def roulette_game(request):
    if 'user_id' not in request.session:
        user = User.objects.create(username="Guest", chipcount=1000)
        request.session['user_id'] = user.id
    else:
        user = User.objects.get(userid=request.session['user_id'])

    balance = user.chipcount
    result = {}

    if request.method == 'POST':
        bet_type = request.POST.get('bet_type')
        value = request.POST.get('value')
        try:
            amount = int(request.POST.get('amount'))
        except (ValueError, TypeError):
            result['error'] = "Invalid bet amount."
            print("Invalid bet amount.")
            return render(request, 'roulette/roulette.html', {'balance': balance, 'result': result})

        if amount > balance:
            result['error'] = "Insufficient balance!"
            print("Insufficient balance!")
        else:
            # Simulate a spin
            spin_number = random.randint(0, 36)
            spin_color = "red" if spin_number % 2 == 0 else "black"
            print(f"Spin Result: Number={spin_number}, Color={spin_color}")

            spin = Roulette.objects.create(number=spin_number, color=spin_color)

            # Maintain a queue of the last 5 spins
            if Roulette.objects.count() > 5:
                oldest_spin = Roulette.objects.order_by('spinid').first()
                oldest_spin.delete()

            # Evaluate the bet
            payout = evaluate_bet(bet_type, value, amount, spin_number, spin_color)
            print(f"Payout: {payout}, Bet Amount: {amount}")

            user.chipcount += payout - amount
            user.save()
            print(f"Updated Chip Count: {user.chipcount}")

            # Save the bet
            UserBet.objects.create(
                userid=user.userid,
                betamount=amount,
                earnings=payout
            )

            result.update({
                'spin_number': spin_number,
                'spin_color': spin_color,
                'payout': payout,
                'new_balance': user.chipcount,
                'won': payout > 0,
                'amount_bet': amount
            })

    # Fetch the last 5 spins
    past_spins = Roulette.objects.all().order_by('-spinid')[:5]
    print(f"Last 5 Spins: {list(past_spins)}")

    # Fetch the user's bets
    user_bets = UserBet.objects.filter(userid=user.userid).order_by('-betid')[:5]
    print(f"Last 5 Bets: {list(user_bets)}")

    return render(request, 'roulette/roulette.html', {
        'balance': user.chipcount,
        'result': result,
        'past_spins': past_spins,
        'user_bets': user_bets,
    })


