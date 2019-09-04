from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model

from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from referral.models import Campaign
from referral.faker_factories import FakeCampaignFactory, faker


class ReferralTest(APITestCase):

    def _create_user(self, password='123456'):
        self.user = get_user_model().objects.create(
            username=faker.user_name(),
            email=faker.email(),
            is_superuser=False,
            is_active=True)
        self.user.set_password(password)
        self.user.save()

        return self.user

    def _do_login(self, user, password='123456'):
        return self.client.login(username=user.username, password=password)

    def setUp(self):
        self._create_user()

    def test_retrieve_user_campaigns(self):
        # PREPARE DATA
        FakeCampaignFactory.create_batch(size=4)
        campaign_1 = Campaign.objects.all()[0]
        campaign_2 = Campaign.objects.all()[1]
        self.user.referrals.add(campaign_1)
        self.user.referrals.add(campaign_2)

        url = reverse('referral:campaign-list')
        self._do_login(self.user)

        # DO ACTION
        response = self.client.get(url)

        # DO ASSERTS
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data), 2)

    def test_user_without_campaigns_get_no_campaigns(self):
        # PREPARE DATA
        FakeCampaignFactory.create_batch(size=4)

        url = reverse('referral:campaign-list')
        self._do_login(self.user)

        # DO ACTION
        response = self.client.get(url)

        # DO ASSERTS
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data), 0)

    def test_retrieve_only_active_campaigns(self):
        # PREPARE DATA
        FakeCampaignFactory.create_batch(size=4)
        campaign_1 = Campaign.objects.all()[0]
        campaign_2 = Campaign.objects.all()[1]
        campaign_2.status = settings.REFERRAL_CAMPAIGN_STATUS_INACTIVE
        campaign_2.save()
        self.user.referrals.add(campaign_1)
        self.user.referrals.add(campaign_2)

        url = reverse('referral:campaign-list')
        self._do_login(self.user)

        # DO ACTION
        response = self.client.get(url)

        # DO ASSERTS
        response_data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response_data), 1)
        self.assertEqual(response_data[0].get('name'), campaign_1.name)

    def test_retrieve_user_campaign_requires_authentication(self):
        # PREPARE DATA
        url = reverse('referral:campaign-list')

        # DO ACTION
        response = self.client.get(url)

        # DO ASSERTS
        self.assertTrue(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('referral.tasks.CampaignSubscribeTask.apply_async')
    def test_retrieve_user_campaign_and_subscribe(self, patch_mock):
        # PREPARE DATA
        campaign_1 = FakeCampaignFactory.create()
        self.user.referrals.add(campaign_1)

        url = reverse('referral:campaign-subscribe', kwargs={'campaign_id': campaign_1.campaign_id})
        self._do_login(self.user)

        # DO ACTION
        data = {
            'rh': 'XXXYYY',
            'conversion': False,
        }
        response = self.client.post(url, data=data)

        # DO ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(patch_mock.called)
