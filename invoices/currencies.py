CURRENCIES = [
    ('USD', 'US Dollar', '$'),
    ('GBP', 'British Pound', '£'),
    ('EUR', 'Euro', '€'),
    ('PKR', 'Pakistani Rupee', '₨'),
    ('INR', 'Indian Rupee', '₹'),
    ('AED', 'UAE Dirham', 'AED'),
    ('SAR', 'Saudi Riyal', 'SAR'),
    ('CAD', 'Canadian Dollar', '$'),
    ('AUD', 'Australian Dollar', '$'),
    ('NZD', 'New Zealand Dollar', '$'),
    ('ZAR', 'South African Rand', 'R'),
    ('NGN', 'Nigerian Naira', '₦'),
    ('KES', 'Kenyan Shilling', 'KSh'),
    ('EGP', 'Egyptian Pound', 'E£'),
    ('PHP', 'Philippine Peso', '₱'),
    ('BDT', 'Bangladeshi Taka', '৳'),
    ('LKR', 'Sri Lankan Rupee', '₨'),
    ('TRY', 'Turkish Lira', '₺'),
    ('CNY', 'Chinese Yuan', '¥'),
    ('JPY', 'Japanese Yen', '¥'),
    ('SGD', 'Singapore Dollar', '$'),
    ('MYR', 'Malaysian Ringgit', 'RM'),
    ('IDR', 'Indonesian Rupiah', 'Rp'),
    ('BRL', 'Brazilian Real', 'R$'),
    ('MXN', 'Mexican Peso', '$'),
    ('QAR', 'Qatari Riyal', 'QAR'),
    ('KWD', 'Kuwaiti Dinar', 'KWD'),
]

CURRENCY_SYMBOLS = {code: sym for code, name, sym in CURRENCIES}


def get_symbol(code):
    return CURRENCY_SYMBOLS.get((code or '').upper(), (code or 'USD') + ' ')
