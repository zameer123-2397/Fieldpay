def account_status(request):
    return {'has_account': bool(request.COOKIES.get('fp_contractor_id'))}
