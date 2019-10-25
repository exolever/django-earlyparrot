from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import TestCase

from unittest.mock import patch

from referral.faker_factories import FakeCampaignFactory, faker
from referral.helpers import normalize_email


class CommandsTestCase(TestCase):

    def create_users_from_csv(self, filepath, password='123456'):
        users = []

        with open(filepath) as file:
            emails = file.readlines()

            for email in emails:
                email = normalize_email(email)

                user = get_user_model().objects.create(
                    username=faker.user_name(),
                    email=email,
                    first_name=faker.first_name(),
                    last_name=faker.last_name(),
                    is_superuser=False,
                    is_active=True)

                user.set_password(password)
                user.save()

                users.append(user)

        return users


    def test_command_add_users_to_campaign(self):
        # PREPARE DATA
        campaign = FakeCampaignFactory.create()
        filepath = './tests/campaign_users.csv'
        users = self.create_users_from_csv(filepath)

        # DO ACTION
        with patch('referral.tasks.subscriber.SubscriberGetTokenTask.apply_async') as patch_task:
            call_command('add_users_to_campaign', '-c', campaign.campaign_id, '-f', filepath)

        # ASSERTS
        for user in users:
            self.assertIn(user, campaign.users.all())

        self.assertEqual(campaign.users.count(), 3)

    def test_command_add_users_to_campaign_to_not_duplicate_users(self):
        # PREPARE DATA
        campaign = FakeCampaignFactory.create()
        filepath = './tests/campaign_users.csv'
        users = self.create_users_from_csv(filepath)

        # DO ACTION
        with patch('referral.tasks.subscriber.SubscriberGetTokenTask.apply_async') as patch_task:
            call_command('add_users_to_campaign', '-c', campaign.campaign_id, '-f', filepath)
            call_command('add_users_to_campaign', '-c', campaign.campaign_id, '-f', filepath)

        # ASSERTS
        self.assertEqual(campaign.users.count(), 3)
