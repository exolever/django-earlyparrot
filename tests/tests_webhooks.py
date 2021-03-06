from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

from mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from referral.faker_factories import FakeCampaignFactory, faker
from referral.models import Campaign


class TestReferralWebhooks(APITestCase):

    def _create_user(self, password='123456'):
        self.user = get_user_model().objects.create(
            email=faker.email(),
            is_superuser=False,
            is_active=True)
        self.user.set_password(password)
        self.user.save()

        return self.user

    def _get_referral_webhook_payload(self, campaign_id=None, email=None):
        return {
            'pointType': 'referrals',
            'point': 3,
            'rewardImage': 'https://mydomain.com/rewardImage.jpg',
            'rewardName': 'Free E-Book',
            'rewardDescription': '',
            'rewardId': '5b8fdb3c6d8c774e5eab7183',
            'campaignId': campaign_id or faker.numerify(),
            'email': email or faker.email(),
            'webHookType': 'NewReward'
        }

    @patch('referral.tasks.subscriber.SubscriberGetTokenTask.apply_async')
    @patch('referral.signals_define.referral_reward_acquired.send')
    def test_referral_webhook_received_launch_signal(self, mock_signal_reward, patch_task):
        # PREPARE DATA
        campaign = FakeCampaignFactory()
        user = self._create_user()
        campaign.add_subscriber(user)
        data = self._get_referral_webhook_payload(
            campaign_id=campaign.campaign_id,
            email=user.email,
        )
        url = reverse('referral:reward-awared')

        # DO ACTION
        response = self.client.post(url, data)

        # DO ASSERTIONS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_signal_reward.called)

    @patch('referral.signals_define.referral_reward_acquired.send')
    def test_work_payload_data_raise_404(self, mock_signal_reward):
        # PREPARE DATA
        data = self._get_referral_webhook_payload()
        url = reverse('referral:reward-awared')

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTIONS
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertFalse(mock_signal_reward.called)
        self.assertFalse(Campaign.objects.filter(campaign_id=data.get('campaignId')).exists())
        self.assertEqual(settings.REFERRAL_NEW_REWARD_AWARED, data.get('webHookType'))

    @patch('referral.signals_define.referral_reward_acquired.send')
    def test_work_payload_data_raise_404_if_user_is_not_subscriber(self, mock_signal_reward):
        # PREPARE DATA
        campaign = FakeCampaignFactory()
        data = self._get_referral_webhook_payload(
            campaign_id=campaign.campaign_id
        )
        url = reverse('referral:reward-awared')

        # DO ACTION
        response = self.client.post(url, data)

        # ASSERTIONS
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Campaign.objects.filter(campaign_id=data.get('campaignId')).exists())
        self.assertFalse(campaign.users.filter(email=data.get('email')).exists())
        self.assertEqual(settings.REFERRAL_NEW_REWARD_AWARED, data.get('webHookType'))
        self.assertFalse(mock_signal_reward.called)
