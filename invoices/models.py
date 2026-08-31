from django.db import models

class Contractor(models.Model):
    name = models.CharField(max_length=100, default='there')
    phone = models.CharField(max_length=20, blank=True)
    cookie_id = models.CharField(max_length=64, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    stripe_link = models.URLField(blank=True)
    square_link = models.URLField(blank=True)
    bank_details = models.TextField(blank=True)
    verification_token = models.CharField(max_length=64, blank=True)
    setup_complete = models.BooleanField(default=False)
    default_currency = models.CharField(max_length=3, default='USD')
    
    
class Invoice(models.Model):
    contractor = models.ForeignKey(Contractor, on_delete=models.CASCADE)
    job_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    customer_phone = models.CharField(max_length=20)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    currency = models.CharField(max_length=3, default='USD')

