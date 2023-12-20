from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path("", HomeView.as_view(), name='home'),
    path("register", Register.as_view(), name='register'),
    path("login", Login.as_view(), name='login'),
    path("login/secure-code", send_secure_code, name='send_secure_code'),
    path("logout", auth_logout, name='logout'),
    path("accounts", AccountsView.as_view(), name='accounts'),
    path("creating-bank-account", creating_bank_account, name='create_account'),
    path("create-card", create_card, name='create_card'),
    path("transactions", TransactionsView.as_view(), name='transactions'),
    path("transactions/<int:active_card>", TransactionsView.as_view(), name='transactions'),
    path("make_transaction", make_transaction, name='make_transaction'),
    path("credit", CreditView.as_view(), name='credit'),
    path("credit-dates", calculate_credit_dates, name='calculate_credit_dates'),
    path("creating-category", create_category, name='add_category'),
    path("deleting-category", delete_category, name='delete_category'),
    path("category/add-transaction", add_transaction, name='add_transaction')
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)