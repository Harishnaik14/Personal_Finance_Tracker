from decimal import Decimal
import requests
from django.core.cache import cache

def get_exchange_rate(target_currency, base_currency='INR'):
    """
    Fetches exchange rate from INR to Target Currency.
    Cached for 24 hours.
    """
    if target_currency == base_currency:
        return 1.0

    cache_key = f'exchange_rate_{base_currency}_{target_currency}'
    rate = cache.get(cache_key)

    if rate:
        return rate

    try:
        # specific hardcoded fallbacks for common currencies to avoid API dependence if possible or as backup
        # But user requested "fetch from server", so we try API first.
        url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
        response = requests.get(url, timeout=5)
        data = response.json()
        rates = data.get('rates', {})
        rate = rates.get(target_currency)
        
        if rate:
            cache.set(cache_key, rate, timeout=86400) # 24 hours
            return rate
            
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")

    # Manual Fallback Map (Approximate)
    fallback_rates = {
        'USD': 0.012,
        'EUR': 0.011,
        'GBP': 0.0095,
        'JPY': 1.75,
        'INR': 1.0
    }
    return fallback_rates.get(target_currency, 1.0)

def convert_amount(amount, target_currency):
    rate = get_exchange_rate(target_currency)
    try:
        return round(float(amount) * rate, 2)
    except (ValueError, TypeError):
        return 0.0

def get_spending_insights(user):
    """
    Analyzes user expenses and provides comparison insights between 
    the current month and the previous month.
    """
    from .models import Transaction
    from django.db.models import Sum
    from django.utils import timezone
    from decimal import Decimal

    now = timezone.now()
    # Current month start
    curr_start = now.replace(day=1)
    
    # Previous month date range
    prev_end = curr_start - timezone.timedelta(days=1)
    prev_start = prev_end.replace(day=1)

    # Fetch expenses by category for current month
    curr_expenses = Transaction.objects.filter(
        user=user,
        category__type='expense',
        date__year=now.year,
        date__month=now.month
    ).values('category__name').annotate(total=Sum('amount'))

    # Fetch expenses by category for previous month
    prev_expenses = Transaction.objects.filter(
        user=user,
        category__type='expense',
        date__year=prev_start.year,
        date__month=prev_start.month
    ).values('category__name').annotate(total=Sum('amount'))

    curr_map = {item['category__name']: float(item['total']) for item in curr_expenses}
    prev_map = {item['category__name']: float(item['total']) for item in prev_expenses}

    all_categories = set(curr_map.keys()) | set(prev_map.keys())
    insights = []

    for cat in all_categories:
        curr_val = curr_map.get(cat, 0.0)
        prev_val = prev_map.get(cat, 0.0)

        if prev_val == 0:
            if curr_val > 0:
                change = 100.0
                status = 'new'
                text = f"{cat} is a new expense this month."
            else:
                continue
        else:
            percent_change = ((curr_val - prev_val) / prev_val) * 100
            change = round(percent_change, 1)

            if change > 0:
                status = 'increase'
                text = f"You spent {change}% more on {cat} this month."
            elif change < 0:
                status = 'decrease'
                text = f"Your {cat} expenses decreased by {abs(change)}%."
            else:
                status = 'neutral'
                text = f"Your spending on {cat} remained the same."

        insights.append({
            'category': cat,
            'current': curr_val,
            'prev': prev_val,
            'change': change,
            'status': status,
            'text': text
        })

    # Summary Insight (Total)
    curr_total = sum(curr_map.values())
    prev_total = sum(prev_map.values())
    total_insight = None

    if prev_total > 0:
        total_change = round(((curr_total - prev_total) / prev_total) * 100, 1)
        if total_change > 0:
            total_insight = {
                'text': f"Overall, your spending increased by {total_change}% compared to last month.",
                'status': 'increase'
            }
        elif total_change < 0:
            total_insight = {
                'text': f"Great job! Your overall spending decreased by {abs(total_change)}%.",
                'status': 'decrease'
            }
    
    return {
        'category_insights': sorted(insights, key=lambda x: abs(x['change']), reverse=True),
        'total_insight': total_insight,
        'has_prev_data': prev_total > 0
    }

def get_ai_suggestions(user):
    """
    Analyzes historical spending (last 6 months) to provide 
    personalized suggestions and predict next month's expenses.
    Pure Python implementation of least squares for trend analysis.
    """
    from .models import Transaction
    from django.db.models import Sum
    from django.utils import timezone
    from datetime import timedelta
    from collections import defaultdict

    now = timezone.now().date()
    # Looking back 6 months
    history_months = []
    for i in range(6, -1, -1): # 6 months back + current month
        d = (timezone.now() - timedelta(days=30*i)).date().replace(day=1)
        history_months.append(d)

    # Aggregate monthly totals
    monthly_totals = []
    category_trends = defaultdict(list)
    
    for m in history_months:
        total = Transaction.objects.filter(
            user=user,
            category__type='expense',
            date__year=m.year,
            date__month=m.month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_totals.append(float(total))

        # Category-wise for trend analysis
        cats = Transaction.objects.filter(
            user=user,
            category__type='expense',
            date__year=m.year,
            date__month=m.month
        ).values('category__name').annotate(total=Sum('amount'))
        for c in cats:
            category_trends[c['category__name']].append(float(c['total']))

    def simple_linear_predict(series):
        if len(series) < 2:
            return series[0] if series else 0.0
        
        # least squares: y = mx + b
        n = len(series)
        x = list(range(n))
        y = series
        
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xx = sum(xi*xi for xi in x)
        sum_xy = sum(xi*yi for xi, yi in zip(x, y))
        
        denominator = (n * sum_xx - sum_x * sum_x)
        if denominator == 0:
            return sum_y / n
            
        m = (n * sum_xy - sum_x * sum_y) / denominator
        b = (sum_y - m * sum_x) / n
        
        prediction = m * n + b # predict next index
        return max(0, prediction)

    # 1. Prediction for Total
    prediction_next = simple_linear_predict(monthly_totals)

    # 2. Category-wise Prediction
    predicted_categories = {}
    for cat, values in category_trends.items():
        # Pad with zeros for months where category wasn't used to get accurate trend
        full_values = [0.0] * (len(history_months) - len(values)) + values
        predicted_categories[cat] = simple_linear_predict(full_values)

    # 3. Savings Suggestions
    suggestions = []
    avg_total = sum(monthly_totals) / len(monthly_totals) if monthly_totals else 0
    
    # Sort categories by total recent spending to find high-impact areas
    top_categories = sorted(category_trends.items(), key=lambda x: sum(x[1]), reverse=True)
    
    for cat, values in top_categories[:3]:
        cat_avg = sum(values) / len(values)
        if cat_avg > 0:
            potential_saving = round(cat_avg * 0.15, 2) # 15% reduction goal
            suggestions.append({
                'icon': '💡',
                'text': f"You can save about 15% on {cat} next month, which is roughly {potential_saving} based on your averages.",
                'type': 'saving'
            })

    if prediction_next > avg_total * 1.1 and avg_total > 0:
        suggestions.append({
            'icon': '📈',
            'text': "Your spending trend is increasing. Try to review your non-essential subscriptions.",
            'type': 'warning'
        })
    elif prediction_next < avg_total * 0.9 and avg_total > 0:
        suggestions.append({
            'icon': '🤖',
            'text': "Great trend! You are on track to spend less than your average next month.",
            'type': 'success'
        })
    elif avg_total == 0:
        suggestions.append({
            'icon': '✨',
            'text': "Start tracking your expenses to see personalized AI insights here!",
            'type': 'info'
        })

    # Historical Data for Chart
    chart_labels = [(m.strftime('%b %Y')) for m in history_months]
    chart_labels.append("Next Month (Est.)")
    
    chart_data = monthly_totals + [round(prediction_next, 2)]

    return {
        'prediction_total': round(prediction_next, 2),
        'predicted_categories': predicted_categories,
        'suggestions': suggestions[:4],
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'historical_avg': round(avg_total, 2)
    }

def init_guest_session(request):
    """
    Initializes the guest session with demo data if it doesn't exist.
    """
    if 'guest_transactions' not in request.session:
        request.session['guest_transactions'] = [
            {'category': {'name': 'Freelance', 'type': 'income'}, 'date': '2023-11-28', 'amount': '1200.00', 'description': 'Project Payment'},
            {'category': {'name': 'Groceries', 'type': 'expense'}, 'date': '2023-11-27', 'amount': '150.00', 'description': 'Supermarket run'},
            {'category': {'name': 'Netflix', 'type': 'expense'}, 'date': '2023-11-25', 'amount': '15.00', 'description': 'Subscription'},
            {'category': {'name': 'Salary', 'type': 'income'}, 'date': '2023-11-20', 'amount': '4000.00', 'description': 'Monthly Salary'},
            {'category': {'name': 'Cafe', 'type': 'expense'}, 'date': '2023-11-18', 'amount': '25.00', 'description': 'Coffee & Snacks'},
        ]
        request.session['guest_currency'] = 'USD'
        request.session.modified = True

def get_guest_data(request):
    """
    Calculates totals and retrieves transactions from session.
    """
    transactions = request.session.get('guest_transactions', [])
    
    income = sum(Decimal(t['amount']) for t in transactions if t['category']['type'] == 'income')
    expense = sum(Decimal(t['amount']) for t in transactions if t['category']['type'] == 'expense')
    balance = Decimal('23490.00') + income - expense # Start with a base opening balance
    
    # Sort by date descending
    sorted_transactions = sorted(transactions, key=lambda x: x['date'], reverse=True)
    
    return {
        'income': income,
        'expense': expense,
        'balance': balance,
        'recent_transactions': sorted_transactions[:5],
        'all_transactions': sorted_transactions
    }

def add_guest_transaction(request, form_data):
    """
    Adds a transaction to the guest session.
    """
    init_guest_session(request)
    
    # Extract data from cleaned_data
    cat_obj = form_data['category']
    if cat_obj:
        cat_data = {'name': cat_obj.name, 'type': cat_obj.type}
    else:
        cat_data = {'name': form_data.get('custom_category') or 'Uncategorized', 'type': 'expense'}

    new_transaction = {
        'category': cat_data,
        'date': str(form_data['date']),
        'amount': str(form_data['amount']),
        'description': form_data['description']
    }
    
    request.session['guest_transactions'].append(new_transaction)
    request.session.modified = True
