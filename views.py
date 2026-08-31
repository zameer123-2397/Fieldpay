import uuid
import secrets
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum
from django.core.mail import send_mail
from django.contrib import messages
from urllib.parse import quote
from .models import Contractor, Invoice
from django.conf import settings
from django.template.loader import render_to_string
from .currencies import CURRENCIES, get_symbol
from .rates import convert

def get_contractor(request):
    cookie_id = request.COOKIES.get('fp_contractor_id')
    if cookie_id:
        contractor = Contractor.objects.filter(cookie_id=cookie_id).first()
        if contractor:
            return contractor, False
    contractor = Contractor.objects.create(cookie_id=str(uuid.uuid4()))
    return contractor, True


def home(request):
    cookie_id = request.COOKIES.get('fp_contractor_id')
    if cookie_id:
        contractor = Contractor.objects.filter(cookie_id=cookie_id).first()
        if contractor and contractor.setup_complete:
            return redirect('dashboard')
    return render(request, 'landing.html')

def dashboard(request):
    contractor, is_new = get_contractor(request)
    generated = None

    if request.method == 'POST' and 'job_name' in request.POST:
        job_name = request.POST.get('job_name')
        price = request.POST.get('price')
        currency = (request.POST.get('currency', 'USD') or 'USD').strip().upper()[:3]
        customer_phone = request.POST.get('customer_phone', '').replace(' ', '').replace('-', '')

        invoice = Invoice.objects.create(
            contractor=contractor, job_name=job_name, price=price,
            currency=currency, customer_phone=customer_phone,
        )
        # NOTE: contractor.default_currency ab yahan overwrite nahi hoti — yehi bug tha

        invoice_url = request.build_absolute_uri(reverse('invoice_detail', args=[invoice.id]))
        message = f"Hi! Your invoice for {job_name} is {get_symbol(currency)}{price}. Pay here: {invoice_url}"
        whatsapp_link = f"https://wa.me/{customer_phone}?text={quote(message)}"
        generated = {
            'invoice': invoice, 'whatsapp_link': whatsapp_link,
            'invoice_url': invoice_url, 'symbol': get_symbol(currency),
        }

    all_invoices = Invoice.objects.filter(contractor=contractor).order_by('-created_at')
    this_month = timezone.now().month
    month_invoices = all_invoices.filter(created_at__month=this_month)

    display_currency = (request.GET.get('display') or contractor.default_currency or 'USD').upper()[:3]

    earned = 0
    pending = 0
    for inv in month_invoices:
        converted = convert(inv.price, inv.currency, display_currency)
        if converted is None:
            continue
        if inv.paid:
            earned += converted
        else:
            pending += converted
    earned = round(earned, 2)
    pending = round(pending, 2)
    sent_count = month_invoices.count()

    recent_customers = []
    seen_phones = set()
    for inv in all_invoices:
        if inv.customer_phone not in seen_phones:
            recent_customers.append(inv)
            seen_phones.add(inv.customer_phone)
        if len(recent_customers) >= 2:
            break

    context = {
        'contractor': contractor,
        'generated': generated,
        'recent_invoices': all_invoices[:5],
        'recent_customers': recent_customers,
        'earned': earned,
        'pending': pending,
        'sent_count': sent_count,
        'currency_symbol': get_symbol(display_currency),
        'display_currency': display_currency,
        'currencies': CURRENCIES,
        'default_currency': contractor.default_currency,
    }
    response = render(request, 'dashboard.html', context)
    if is_new:
        response.set_cookie('fp_contractor_id', contractor.cookie_id, max_age=60 * 60 * 24 * 400)
    return response


def setup_account(request):
    if request.method == 'POST':
        contractor, is_new = get_contractor(request)
        contractor.email = request.POST.get('email', '').strip()
        contractor.stripe_link = request.POST.get('stripe_link', '').strip()
        contractor.square_link = request.POST.get('square_link', '').strip()
        contractor.bank_details = request.POST.get('bank_details', '').strip()
        contractor.verification_token = secrets.token_urlsafe(24)
        contractor.save()

        verify_url = request.build_absolute_uri(reverse('verify_account', args=[contractor.verification_token]))
        html_content = render_to_string('emails/verify_email.html', {'verify_url': verify_url})
        send_mail(
            'Verify your FieldPay account',
            f'Tap to finish setup: {verify_url}',
            settings.DEFAULT_FROM_EMAIL,
            [contractor.email],
            fail_silently=True,
            html_message=html_content,
        )
        messages.success(request, 'Verification link sent - check your email')
        response = redirect('dashboard')
        if is_new:
            response.set_cookie('fp_contractor_id', contractor.cookie_id, max_age=60 * 60 * 24 * 400)
        return response
    return redirect('dashboard')
    
    
def login_link(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        contractor = Contractor.objects.filter(email=email).first()
        if contractor:
            contractor.verification_token = secrets.token_urlsafe(24)
            contractor.save()

            verify_url = request.build_absolute_uri(reverse('verify_account', args=[contractor.verification_token]))

            html_content = render_to_string('emails/login_email.html', {'verify_url': verify_url})

            send_mail(
                'Your FieldPay login link',
                f'Tap to log in: {verify_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
                html_message=html_content,
            )

        messages.success(request, 'If that email has an account, a link has been sent')
        return redirect('dashboard')
    return redirect('dashboard')


def verify_account(request, token):
    contractor = Contractor.objects.filter(verification_token=token).first()
    if not contractor:
        messages.error(request, 'That link is invalid or expired')
        return redirect('home')

    contractor.setup_complete = True
    contractor.verification_token = ''
    contractor.save()
    response = redirect('dashboard')
    response.set_cookie('fp_contractor_id', contractor.cookie_id, max_age=60 * 60 * 24 * 400)
    messages.success(request, "You're verified — all set")
    return response


def invoice_detail(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST' and 'mark_paid' in request.POST:
        invoice.paid = True
        invoice.save()
        return redirect('invoice_detail', invoice_id=invoice.id)
    return render(request, 'invoice_detail.html', {'invoice': invoice, 'symbol': get_symbol(invoice.currency)})

def settings_page(request):
    contractor, _ = get_contractor(request)
    if request.method == 'POST' and 'delete_data' in request.POST:
        contractor.delete()
        response = redirect('home')
        response.delete_cookie('fp_contractor_id')
        return response
    invoice_count = Invoice.objects.filter(contractor=contractor).count()
    return render(request, 'settings.html', {'invoice_count': invoice_count, 'contractor': contractor})


def features_page(request):
    return render(request, 'features.html')


def why_fieldpay_page(request):
    return render(request, 'why_fieldpay.html')


def pricing_page(request):
    return render(request, 'pricing.html')
    
def privacy_page(request):
    return render(request, 'privacy.html')


def terms_page(request):
    return render(request, 'terms.html')


def contact_page(request):
    return render(request, 'contact.html')
    
    
def logout_view(request):
    response = redirect('home')
    response.delete_cookie('fp_contractor_id')
    return response
    
    
