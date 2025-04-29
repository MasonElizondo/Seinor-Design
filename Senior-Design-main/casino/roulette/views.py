from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User as AuthUser
from django.http import JsonResponse  # Import JsonResponse
from django.shortcuts import render
from .models import Roulette, UserBets
import random
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.db import transaction
from django.db.models import Max
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

def get_color(number):
    if number == 0:
        return 'green'
    return 'red' if number in RED_NUMBERS else 'black'

def spin_roulette():
    number = random.randint(0, 36)
    color = get_color(number)
    return number, color

def index(request):
    return render(request, 'index.html')

def create_account(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        if password != confirm_password:
            return render(request, 'createAccount.html', {'error': 'Passwords do not match.'})

        if username and password:
            try:

                user = AuthUser.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name)
                user.save()
                #initialize the user's chip count
                UserBets.objects.create(userid=user.id, betid=1, betamount=0, earnings=0, chipcount=1000)
                # Store user ID in session
                request.session['user_id'] = user.userid

                # Redirect to the roulette page with the user's balance
                return redirect('/login/')
            except Exception as e:
                # Handle errors (e.g., username already exists)
                return render(request, 'createAccount.html', {'error': str(e)})

    # Render the create account page if the request method is not POST
    return render(request, 'createAccount.html')


@login_required
def roulette(request):
    print("Roulette view called")
    if 'balance' not in request.session:
        request.session['balance'] = 1000  # Starting balance

    if 'last_spins' not in request.session:
        request.session['last_spins'] = []  # Initialize last spins

    balance = request.session['balance']
    last_spins = request.session['last_spins']
    result = {}

    # Prepare numbers as a list of rows (3 rows, 12 numbers each)
    numbers = [list(range(i, i + 12)) for i in range(1, 37, 12)]
    red_numbers = list(RED_NUMBERS)  # Convert set to list for template rendering

    if request.method == 'POST':
        user = request.user  # Get the authenticated user
        bet_type = request.POST.get('bet_type')
        value = request.POST.get('value')
        amount = int(request.POST.get('amount', 0))

        # Debugging: Print the received data
        print(f"Received bet: type={bet_type}, value={value}, amount={amount}, user_id={user.id}")

        if amount > balance:
            result['error'] = "Insufficient balance!"
        else:
            with transaction.atomic():
                # Spin the roulette
                number, spin_color = spin_roulette()

                # Save the spin result to the Roulette table
                spin = Roulette.objects.create(number=number, color=spin_color)

                # Calculate payout
                payout = 0
                if bet_type == 'number' and value.isdigit() and int(value) == number:
                    payout = amount * 35
                elif bet_type == 'color' and value.lower() == spin_color:
                    payout = amount * 2
                elif bet_type == 'parity':
                    if value == 'even' and number % 2 == 0:
                        payout = amount * 2
                    elif value == 'odd' and number % 2 != 0:
                        payout = amount * 2
                elif bet_type == 'range':
                    if value == '1-18' and 1 <= number <= 18:
                        payout = amount * 2
                    elif value == '19-36' and 19 <= number <= 36:
                        payout = amount * 2

                # Update balance
                balance += payout - amount
                request.session['balance'] = balance

                # Update last spins
                last_spins.append({'number': number, 'color': spin_color})
                if len(last_spins) > 5:
                    last_spins.pop(0)
                request.session['last_spins'] = last_spins

                # Save the bet to the database
                try:
                    max_betid = UserBets.objects.aggregate(Max('betid'))['betid__max']
                    next_betid = max_betid + 1 if max_betid else 1
                    UserBets.objects.create(
                        userid=user.id,  # Use the authenticated user's ID
                        betid=next_betid,
                        betamount=amount,
                        earnings=payout,  # Store the payout as earnings
                        chipcount=balance  # Store the updated balance
                    )
                    print("Bet saved successfully")
                except Exception as e:
                    print(f"Error saving bet: {e}")
                    return JsonResponse({'success': False, 'message': 'Error saving bet.'})

                # Prepare the result
                result = {
                    'success': True,
                    'number': number,
                    'spin_color': spin_color,
                    'payout': payout,
                    'new_balance': balance,
                    'last_spins': last_spins,
                }
                return JsonResponse(result)

    # Handle GET request: Render the roulette page
    return render(request, 'roulette/roulette.html', {
        'balance': balance,
        'last_spins': last_spins,
        'numbers': numbers,  # Pass the list of rows to the template
        'red_numbers': red_numbers,  # Pass red numbers to the template
    })