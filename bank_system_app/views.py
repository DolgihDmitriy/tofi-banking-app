from datetime import date, datetime, timedelta
from dateutil.relativedelta import *
from decimal import *
import hashlib
from http.client import HTTPResponse
import random
import math
from typing import Any
from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse, JsonResponse
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout, login
from django.core.mail import send_mail

from .models import *
from .forms import RegisterForm, LoginForm


class HomeView(TemplateView):
    template_name = 'main/index.html'

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if (user.is_authenticated):
            if Card.objects.filter(user=user).exists():
                card = Card.objects.filter(user=user)
                context['card'] = card

        return context
    


class Register(CreateView):
    form_class = RegisterForm
    template_name = 'register/index.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)

        return redirect('home')


class Login(LoginView):
    form_class = LoginForm
    template_name = 'login/index.html'

    def get_success_url(self):

        user = self.request.user
        user.secure_code = None
        user.save()

        return reverse_lazy('home')

def send_secure_code(request):
    if request.method == 'POST':
        code = str(random.randint(10000,99999))
        user = User.objects.get(username=request.POST['username'])
        send_mail('TofiBank secure code', 'Your secure code for authentication: ' + code, 'navis1mplegod@gmail.com', [user.email], fail_silently=False)

        user.secure_code = code
        user.save()
    
    return HttpResponse(200)

def auth_logout(request):
    if request.method == 'POST':
        logout(request)

    return redirect('home')


def creating_bank_account(request):
    if request.method == 'POST':
        new_account = Account.objects.create(user=request.user)
        account_number = str(new_account.id).zfill(16)
        groups_of_4 = [account_number[i:i+4] for i in range(0, len(account_number), 4)]
        account_number = ''.join(groups_of_4)
        new_account.account_number = account_number
        new_account.save()

        return redirect('accounts')
    else:
        return redirect('home')


class AccountsView(TemplateView):
    template_name = 'accounts/index.html'

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)

        user = self.request.user

        if (user.is_authenticated):        
            if Account.objects.filter(user=user).exists():
                accounts = Account.objects.filter(user=user)
                context['accounts'] = accounts

        return context
    

def create_card(request):
    if request.method == 'POST':
        account = Account.objects.get(pk=request.POST['account_id'])

        expire = date(datetime.now().year + 3, datetime.now().month, 31)

        cvv_code_source = random.randint(0, 999)
        cvv_code = str(cvv_code_source).zfill(3)
        cvv_code = hashlib.sha256(cvv_code.encode('utf-8')).hexdigest()

        new_card = Card.objects.create(
            account=account,
            user=request.user,
            first_name=request.user.first_name,
            last_name=request.user.last_name,
            expire_date=expire,
            cvv_code=cvv_code)
        
        number = str(new_card.id).zfill(12)
        bank_number = '4255'
        groups_of_4 = [number[i:i+4] for i in range(0, len(number), 4)]
        number = ''.join([bank_number, (''.join(groups_of_4))])

        new_card.number = number

        new_card.save()

    return render(request, 'card/index.html', context={'card': new_card, 'cvv_code_source': cvv_code_source})


class CreatedCard(TemplateView):
    template_name = 'card/index.html'

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)

        return context
    

class TransactionsView(TemplateView):

    template_name = 'transactions/index.html'

    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)

        user = self.request.user

        if (user.is_authenticated):        
            if Card.objects.filter(user=user).exists():
                cards = Card.objects.filter(user=user)
                context['cards'] = cards
                transactions = Transactions.objects.filter(user=user).order_by('-date')
                context['transactions'] = transactions

                if ('active_card' not in context):
                    context['active_card'] = 1

                categories = Categories.objects.filter(user=user)
                context['categories'] = categories
        return context
    

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)


def create_category(request):
    if request.method == 'POST':
        category = Categories.objects.create(user=request.user,
                                          percent=10,
                                          name=request.POST['category_name'],
                                          amount=Decimal(request.POST['category_sum']),
                                          current_sum=Decimal(request.POST['category_sum']))
    return redirect("transactions")
    

def delete_category(request):
    if request.method == 'POST':

        Categories.objects.get(pk=int(request.POST["category_id"])).delete()

        return redirect('transactions')


def add_transaction(request):
    if request.method == 'POST':
        category_id = request.POST['category_id']
        transaction_id = request.POST['transaction_id']
        prev_category_id = request.POST['prev_category_id']

        transaction = Transactions.objects.get(pk=transaction_id)

        if int(prev_category_id) != -1:
            
            prev_category = Categories.objects.get(pk=prev_category_id)
            prev_category.current_sum += transaction.amount
            prev_category.save()

        if int(category_id) != -1:
            category = Categories.objects.get(pk=category_id)
            category.current_sum -= transaction.amount
            transaction.category = category
            category.save()
        else:
            transaction.category = None

        transaction.save()

        response_data = {'category_id': category.id, 'transaction_sum': transaction.amount, 'prev_category_id': prev_category_id }

        return JsonResponse(response_data)


def make_transaction(request):
    if request.method == 'POST':
        sender_card = Card.objects.get(number=request.POST['sender_card'])
        receiver_card = Card.objects.get(number=request.POST['card_number'])

        sender_card.account.balance -= Decimal(request.POST['sum'])
        receiver_card.account.balance += Decimal(request.POST['sum'])

        sender_card.account.save()
        receiver_card.account.save()

        transaction = Transactions.objects.create(user=request.user,
                                                  amount=Decimal(request.POST['sum']),
                                                  card_from=sender_card,
                                                  card_to=receiver_card)
        transaction.save()

    return redirect('transactions') 


class CreditView(TemplateView):
    
    template_name = 'credit/index.html'

def generate_dates(start_date, num_dates):
    dates = []
    current_date = start_date
    for _ in range(num_dates):
        dates.append(current_date)
        # Добавим 1 месяц к текущей дате
        current_date = current_date + relativedelta(months=1)
    return dates


def calculate_credit_dates(request):
    if request.method == 'POST':
        
        credit_sum = Decimal(request.POST['credit_sum'])
        credit_term = int(request.POST['credit_term'])
        credit_interest_rate = Decimal(request.POST['credit_interest_rate'])
        monthly_payment = Decimal(request.POST['monthly_payment'])

        credit = Credit.objects.create(credit_sum=credit_sum,
                                       credit_term=credit_sum,
                                       percent=credit_interest_rate,
                                       user=request.user,
                                       start_payment_date=datetime.now())
        
        start_date = datetime.now() + relativedelta(months=1)
        
        credit_data = {}
        
        current_date = start_date
        owed_sum = monthly_payment * credit_term
        
        for i in range(credit_term):
            interest_payment = (owed_sum / credit_term) * (credit_interest_rate / 100)
            debt_payment = monthly_payment - interest_payment
            
            debt_payment = math.floor(debt_payment * 100) / 100
            interest_payment = math.floor(interest_payment * 100) / 100
            
            credit_data[i] = {}
            credit_data[i]["payment_date"] = current_date
            credit_data[i]["payment_sum"] = monthly_payment
            credit_data[i]["debt_payment"] = debt_payment
            credit_data[i]["interest_payment"] = interest_payment
            credit_data[i]["owed_sum"] = owed_sum
            
            current_date = current_date + relativedelta(months=1)
            owed_sum -= monthly_payment
    
        generated_dates = generate_dates(start_date, credit_term)

        return render(request, 'credit/dates.html', context={'credit_data': credit_data})