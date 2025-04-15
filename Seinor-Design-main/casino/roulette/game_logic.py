import random
from django.shortcuts import render

ROULETTE_NUMBERS = list(range(0, 37)) + ['00']
COLORS = {n: 'red' if n % 2 == 0 else 'black' for n in range(1, 37)}
COLORS.update({0: 'green', '00': 'green'})

def spin_roulette():
    number = random.choice(ROULETTE_NUMBERS)
    color = COLORS[number] if number in COLORS else 'green'
    return {"number": number, "color": color}


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

def evaluate_bet(bet, result_number, result_color):
    bet_type = bet['type']
    value = bet['value']
    amount = int(bet['amount'])
    payout = 0

    if bet_type == 'straight':
        if int(value) == result_number:
            payout = amount * 35

    elif bet_type == 'color':
        if value == result_color:
            payout = amount * 1

    elif bet_type == 'even_odd':
        if result_number != 0:
            if value == 'even' and result_number % 2 == 0:
                payout = amount * 1
            elif value == 'odd' and result_number % 2 == 1:
                payout = amount * 1

    elif bet_type == 'dozen':
        if value == '1st' and 1 <= result_number <= 12:
            payout = amount * 2
        elif value == '2nd' and 13 <= result_number <= 24:
            payout = amount * 2
        elif value == '3rd' and 25 <= result_number <= 36:
            payout = amount * 2

    elif bet_type == 'column':
        column_map = {
            '1st': [1,4,7,10,13,16,19,22,25,28,31,34],
            '2nd': [2,5,8,11,14,17,20,23,26,29,32,35],
            '3rd': [3,6,9,12,15,18,21,24,27,30,33,36]
        }
        if result_number in column_map.get(value, []):
            payout = amount * 2

    return payout


def roulette_game(request):
    if 'balance' not in request.session:
        request.session['balance'] = 1000  # starting chips

    balance = request.session['balance']
    result = {}

    if request.method == 'POST':
        bet_type = request.POST.get('bet_type')
        value = request.POST.get('value')
        try:
            amount = int(request.POST.get('amount'))
        except (ValueError, TypeError):
            result['error'] = "Invalid bet amount."
            return render(request, 'roulette/roulette.html', {'balance': balance, 'result': result})

        if amount > balance:
            result['error'] = "Insufficient balance!"
            return render(request, 'roulette/roulette.html', {'balance': balance, 'result': result})

        # Get spin result from the frontend
        try:
            spin_result_number = int(request.POST.get('spin_result_number'))
            spin_result_color = request.POST.get('spin_result_color')

            # Validate spin result
            if spin_result_number < 0 or spin_result_number > 36:
                raise ValueError("Invalid spin result number.")
            if spin_result_color not in ['red', 'black', 'green']:
                raise ValueError("Invalid spin result color.")
        except (ValueError, TypeError):
            result['error'] = "Invalid spin result."
            return render(request, 'roulette/roulette.html', {'balance': balance, 'result': result})

        # Check for win
        won = False
        payout = 0
        if bet_type == 'straight':
            try:
                if int(value) == spin_result_number:
                    won = True
                    payout = 35 * amount
            except ValueError:
                result['error'] = "Invalid number bet."
        elif bet_type == 'color':
            if value == spin_result_color:
                won = True
                payout = amount * 1
        elif bet_type == 'even_odd':
            if spin_result_number != 0:
                if value == 'even' and spin_result_number % 2 == 0:
                    won = True
                    payout = amount * 1
                elif value == 'odd' and spin_result_number % 2 == 1:
                    won = True
                    payout = amount * 1
        elif bet_type == 'dozen':
            if value == '1st' and 1 <= spin_result_number <= 12:
                won = True
                payout = amount * 2
            elif value == '2nd' and 13 <= spin_result_number <= 24:
                won = True
                payout = amount * 2
            elif value == '3rd' and 25 <= spin_result_number <= 36:
                won = True
                payout = amount * 2
        elif bet_type == 'column':
            column_map = {
                '1st': [1, 4, 7, 10, 13, 16, 19, 22, 25, 28, 31, 34],
                '2nd': [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35],
                '3rd': [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36]
            }
            if spin_result_number in column_map.get(value, []):
                won = True
                payout = amount * 2

        # Update balance
        if won:
            balance += payout
        else:
            balance -= amount
        request.session['balance'] = balance

        result.update({
            'spin_result': spin_result_number,
            'spin_color': spin_result_color,
            'won': won,
            'payout': payout if won else 0,
            'amount_bet': amount,
            'new_balance': balance
        })

    return render(request, 'roulette/roulette.html', {
        'balance': balance,
        'result': result
    })
