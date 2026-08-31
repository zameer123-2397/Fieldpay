import requests
from django.core.cache import cache


def get_rates(base='USD'):
    cache_key = f'fx_rates_{base}'
    rates = cache.get(cache_key)
    if rates:
        return rates
    try:
        resp = requests.get(f'https://api.exchangerate-api.com/v4/latest/{base}', timeout=5)
        rates = resp.json().get('rates', {})
        cache.set(cache_key, rates, 60 * 60 * 24)  # 24 hours
    except Exception:
        rates = {}
    return rates


def convert(amount, from_currency, to_currency):
    from_currency = (from_currency or 'USD').upper()
    to_currency = (to_currency or 'USD').upper()
    if from_currency == to_currency:
        return round(float(amount), 2)
    rates = get_rates(from_currency)
    rate = rates.get(to_currency)
    if not rate:
        return None
    return round(float(amount) * rate, 2)