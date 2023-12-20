from django.test import TestCase, Client
from django.urls import reverse
from decimal import *
from .models import *
from datetime import date, datetime, timedelta
import random
import hashlib

class BankTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('test_user', first_name="Дмитрий", last_name="Дмитриев", father_name="Дмитриевич", password='testpass')
        self.client.login(username='test_user', password='testpass')

        self.client.post(reverse('create_account'))
        self.user_account = Account.objects.get(user=self.user)
        response = self.client.post(reverse('create_card'), {'account_id': self.user_account.id})
        self.user_card = Card.objects.get(account=self.user_account)
        self.user_card.balance = Decimal(10000)

        self.receiver_user = User.objects.create_user(identity_number='5171202PB113B3',
                                                      identity_document_number='MC3044487', 
                                                      username='second_user', first_name="Олег", 
                                                      last_name="Олегов", 
                                                      father_name="Олегович", 
                                                      password='testpass',
                                                      email="sakovnv@mail.ru",
                                                      phone_number="375256403656")
        self.receiver_account = Account.objects.create(user=self.receiver_user, account_number="1234123412341234", balance=Decimal(1000))

        cvv_code_source = random.randint(0, 999)
        cvv_code = str(cvv_code_source).zfill(3)
        cvv_code = hashlib.sha256(cvv_code.encode('utf-8')).hexdigest()

        self.receiver_card = Card.objects.create(user=self.receiver_user, 
                                                 first_name="Oleg", 
                                                 last_name="Olegov",
                                                 number="1234432112344321",
                                                 expire_date=date(datetime.now().year + 3, datetime.now().month, 31),
                                                 cvv_code=cvv_code,
                                                 account=self.receiver_account)

    def tearDown(self):
        self.client.logout()

    def test_main_view(self):
        response = self.client.get(f'')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'main/index.html')
        
    def test_register_view(self):
        response = self.client.get(f'/register')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register/index.html')

    def test_login_view(self):
        response = self.client.get(f'/login')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login/index.html')

    def test_bank_account(self):
        response = self.client.post(reverse('create_account'))
        self.assertEqual(response.status_code, 302)

    def test_create_card(self):
        self.client.post(reverse('create_account'))
        self.account = Account.objects.get(pk=2)
        response = self.client.post(reverse('create_card'), {'account_id': self.account.id})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'card/index.html')

        self.assertTrue(Card.objects.filter(account=self.account, user=self.user).exists())

    def test_auth_logout(self):
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_create_delete_category(self):
        response = self.client.post(reverse('add_category'), {'category_name': 'category1', 'category_sum': '300'})
        self.assertEqual(Categories.objects.all().count(), 1)
        self.category = Categories.objects.all().first()
        response = self.client.post(reverse('delete_category'), {'category_id': self.category.id})
        self.assertEqual(Categories.objects.all().count(), 0)

    def test_make_transaction(self):
        response = self.client.post(reverse('make_transaction'), {'sender_card': self.user_card.number, 'card_number': self.receiver_card.number, 'sum': '700'})
        self.assertEqual(Transactions.objects.all().count(), 1)

    def test_add_transaction(self):
        response = self.client.post(reverse('make_transaction'), {'sender_card': self.user_card.number, 'card_number': self.receiver_card.number, 'sum': '700'})
        self.client.post(reverse('add_category'), {'category_name': 'category1', 'category_sum': '300'})
        self.category = Categories.objects.all().first()
        response = self.client.post(reverse('add_transaction'), {'category_id': self.category.id, 'transaction_id': '1', 'prev_category_id': '-1'})
        self.assertTrue(Transactions.objects.all().first().category == self.category)