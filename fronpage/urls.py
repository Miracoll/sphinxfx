from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='front-home'),
    path('contact-us/', views.contact, name='front-contact'),
    path('doge-mining/', views.doge, name='front-doge'),
    path('bitcoin-mining/', views.bitcoin, name='front-bitcoin'),
    path('mining/', views.aboutMining, name='front-mining'),
    path('responsible-trading/', views.responsibleTrading, name='front-responsible'),
    path('what-is-leverage/', views.whatIsLeverage, name='front-leverage'),
    path('copy-expert-traders/', views.copyExpertTrades, name='front-copy'),
    path('options-trading/', views.optionsTrading, name='front-option'),
    path('crypto-trading/', views.cryptoTrading, name='front-crypto'),
    path('stock-trading/', views.stockTrading, name='front-stock'),
    path('forex-trading/', views.forexTrading, name='front-forex'),
    path('general-risk/', views.generalRisk, name='front-risk'),
    path('term-of-service/', views.termOfService, name='front-term'),
    path('privacy-policy/', views.privacyPolicy, name='front-policy'),
    path('cookie/', views.cookie, name='front-cookie'),
    path('about-us/', views.about, name='front-about'),
]
