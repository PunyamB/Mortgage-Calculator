import numpy as np
import pandas as pd


def calculate_payment(principal, annual_rate, years, frequency='monthly'):
    freq_map = {'monthly': 12, 'quarterly': 4, 'annual': 1}
    periods_per_year = freq_map[frequency.lower()]
    
    y = annual_rate / periods_per_year
    n = years * periods_per_year
    
    if y == 0:
        payment = principal / n
    else:
        payment = principal * (y * (1 + y)**n) / ((1 + y)**n - 1)
    
    return payment, y, n


def calculate_outstanding_pv(payment, y, n, k):
    remaining_periods = n - k
    
    if remaining_periods == 0:
        return 0.0
    
    if y == 0:
        outstanding = payment * remaining_periods
    else:
        outstanding = payment * ((1 + y)**remaining_periods - 1) / (y * (1 + y)**remaining_periods)
    
    return outstanding


def generate_amortization_schedule(principal, annual_rate, years, frequency='monthly'):
    payment, y, n = calculate_payment(principal, annual_rate, years, frequency)
    
    schedule_data = []
    outstanding_prev = principal
    cumulative_interest = 0.0
    cumulative_principal = 0.0
    
    for k in range(1, n + 1):
        interest_paid = outstanding_prev * y
        principal_paid = payment - interest_paid
        pv_principal = principal_paid / (1 + y)**k
        outstanding_balance = calculate_outstanding_pv(payment, y, n, k)
        
        cumulative_interest += interest_paid
        cumulative_principal += principal_paid
        
        schedule_data.append({
            'Payment_Number': k,
            'Payment_Amount': payment,
            'Interest_Paid': interest_paid,
            'Principal_Paid': principal_paid,
            'PV_of_Principal': pv_principal,
            'Outstanding_Balance': outstanding_balance,
            'Cumulative_Interest': cumulative_interest,
            'Cumulative_Principal': cumulative_principal
        })
        
        outstanding_prev = outstanding_balance
    
    df = pd.DataFrame(schedule_data)
    return df, payment, y, n


def calculate_accelerated_payoff(principal, annual_rate, original_payment, increased_payment, frequency='monthly'):
    freq_map = {'monthly': 12, 'quarterly': 4, 'annual': 1}
    periods_per_year = freq_map[frequency.lower()]
    y = annual_rate / periods_per_year
    
    min_payment = principal * y
    if increased_payment <= min_payment:
        return None, None, None, None
    
    if y == 0:
        n_new = principal / increased_payment
    else:
        n_new = np.log(increased_payment / (increased_payment - principal * y)) / np.log(1 + y)
    
    n_new = int(np.ceil(n_new))
    
    schedule_data = []
    outstanding = principal
    cumulative_interest = 0.0
    
    for k in range(1, n_new + 1):
        interest_paid = outstanding * y
        
        if k == n_new:
            principal_paid = outstanding
            actual_payment = outstanding + interest_paid
        else:
            principal_paid = increased_payment - interest_paid
            actual_payment = increased_payment
        
        pv_principal = principal_paid / (1 + y)**k
        outstanding -= principal_paid
        cumulative_interest += interest_paid
        
        schedule_data.append({
            'Payment_Number': k,
            'Payment_Amount': actual_payment,
            'Interest_Paid': interest_paid,
            'Principal_Paid': principal_paid,
            'PV_of_Principal': pv_principal,
            'Outstanding_Balance': max(0, outstanding),
            'Cumulative_Interest': cumulative_interest
        })
    
    new_df = pd.DataFrame(schedule_data)
    
    original_schedule, _, _, _ = generate_amortization_schedule(principal, annual_rate, 
                                                                 int(n_new / periods_per_year) + 5, 
                                                                 frequency)
    
    periods_saved = len(original_schedule) - n_new
    original_total_interest = original_schedule['Cumulative_Interest'].iloc[-1]
    new_total_interest = new_df['Cumulative_Interest'].iloc[-1]
    interest_saved = original_total_interest - new_total_interest
    
    return n_new, periods_saved, interest_saved, new_df


def format_currency(value):
    return f"${value:,.2f}"


def format_percentage(value):
    return f"{value * 100:.4f}%"

