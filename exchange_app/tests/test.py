from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from exchange_app.models import Ad, ExchangeProposal


class AdTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='rita', password='testpass')
        self.ad = Ad.objects.create(
            title='Test Ad',
            description='Test Description',
            image_url='http://example.com/image.jpg',
            category='books',
            condition='new',
            user=self.user,
        )

    def test_ad_list_view(self):
        response = self.client.get(reverse('ad-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.ad.title)

    def test_ad_create_view_authenticated(self):
        self.client.login(username='rita', password='testpass')
        response = self.client.post(reverse('ad-create'), {
            'title': 'New Ad',
            'description': 'Some description',
            'image_url': 'http://example.com/new.jpg',
            'category': 'electronics',
            'condition': 'used'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Ad.objects.filter(title='New Ad').exists())

    def test_ad_update_view_permission(self):
        self.client.login(username='rita', password='testpass')
        response = self.client.post(reverse('ad-update', args=[self.ad.pk]), {
            'title': 'Updated Title',
            'description': 'Updated desc',
            'image_url': 'http://example.com/img.jpg',
            'category': 'books',
            'condition': 'used',
        })
        self.assertEqual(response.status_code, 302)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Updated Title')

    def test_ad_delete_view_permission(self):
        self.client.login(username='rita', password='testpass')
        response = self.client.post(reverse('ad-delete', args=[self.ad.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Ad.objects.filter(pk=self.ad.pk).exists())


class AdditionalAdTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='rita', password='testpass')
        self.ad = Ad.objects.create(
            title='Test Ad',
            description='Test Description',
            image_url='http://example.com/image.jpg',
            category='books',
            condition='new',
            user=self.user,
        )

    def test_ad_list_filter_by_category(self):
        Ad.objects.create(title='Other Ad', description='...', category='electronics', condition='new', user=self.user)
        response = self.client.get(reverse('ad-list'), {'category': 'books'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ad')
        self.assertNotContains(response, 'Other Ad')

    def test_ad_list_filter_by_condition(self):
        Ad.objects.create(title='Used Book', description='desc', category='books', condition='used', user=self.user)
        response = self.client.get(reverse('ad-list'), {'condition': 'new'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Ad')
        self.assertNotContains(response, 'Used Book')

    def test_ad_create_view_unauthenticated(self):
        response = self.client.get(reverse('ad-create'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('ad-list'))

    def test_ad_update_view_forbidden_for_other_user(self):
        other_user = User.objects.create_user(username='other', password='testpass')
        self.client.login(username='other', password='testpass')
        response = self.client.post(reverse('ad-update', args=[self.ad.pk]), {
            'title': 'Hacked!',
            'description': '...',
            'image_url': 'http://example.com/img.jpg',
            'category': 'books',
            'condition': 'used',
        })
        self.assertEqual(response.status_code, 403)

    def test_ad_delete_nonexistent(self):
        self.client.login(username='rita', password='testpass')
        response = self.client.post(reverse('ad-delete', args=[999]))
        self.assertEqual(response.status_code, 404)


class SignUpTests(TestCase):
    def test_signup_view(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'ComplexPass123',
            'password2': 'ComplexPass123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())


class ExchangeProposalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='rita', password='testpass')
        self.user2 = User.objects.create_user(username='alex', password='testpass')
        self.ad1 = Ad.objects.create(title='Ad1', description='desc', category='books', condition='used', user=self.user1)
        self.ad2 = Ad.objects.create(title='Ad2', description='desc', category='books', condition='used', user=self.user2)

    def test_exchange_proposal_create(self):
        self.client.login(username='rita', password='testpass')
        response = self.client.post(reverse('proposal-create'), {
            'ad_sender': self.ad1.pk,
            'ad_receiver': self.ad2.pk,
            'message': 'Would you like to exchange?'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExchangeProposal.objects.count(), 1)

    def test_proposal_list_filter_sent(self):
        proposal = ExchangeProposal.objects.create(ad_sender=self.ad1, ad_receiver=self.ad2, status='pending')
        self.client.login(username='rita', password='testpass')
        response = self.client.get(reverse('proposal-list'), {'direction': 'sent'})
        self.assertContains(response, proposal.comment)


class AdditionalExchangeProposalTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='rita', password='testpass')
        self.other_user = User.objects.create_user(username='alex', password='testpass')
        self.ad = Ad.objects.create(title='Test Ad', description='...', category='books', condition='new', user=self.user)

    # def test_proposal_create_invalid_ad_sender(self):
    #     self.client.login(username='alex', password='testpass')
    #     response = self.client.post(reverse('proposal-create'), {
    #         'ad_sender': self.ad.pk,
    #         'ad_receiver': self.ad.pk,
    #         'message': 'Fake sender attempt',
    #     })
    #     self.assertFormError(response, 'form', None, 'Нельзя создавать предложение на обмен с самим собой')


    # def test_proposal_status_update_forbidden_for_non_receiver(self):
    #     self.client.login(username='rita', password='testpass')
    #     proposal = ExchangeProposal.objects.create(ad_sender=self.ad, ad_receiver=self.ad, status='pending')
    #     hacker = User.objects.create_user(username='hacker', password='testpass')
    #     self.client.login(username='hacker', password='testpass')
    #     response = self.client.post(reverse('proposal-update', args=[proposal.pk]), {
    #         'status': 'accepted',
    #     })
    #     self.assertEqual(response.status_code, 404)
