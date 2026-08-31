from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('features/', views.features_page, name='features'),
    path('why-fieldpay/', views.why_fieldpay_page, name='why_fieldpay'),
    path('pricing/', views.pricing_page, name='pricing'),
    path('settings/', views.settings_page, name='settings'),
    path('setup-account/', views.setup_account, name='setup_account'),
    path('login-link/', views.login_link, name='login_link'),
    path('verify/<str:token>/', views.verify_account, name='verify_account'),
    path('privacy/', views.privacy_page, name='privacy'),
    path('terms/', views.terms_page, name='terms'),
    path('contact/', views.contact_page, name='contact'),
    path('logout/', views.logout_view, name='logout'),
]