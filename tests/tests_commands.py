from django.core.management import call_command
from django.test import TestCase

from referral.faker_factories import FakeCampaignFactory

from .helpers import create_users_from_csv


class CommandsTestCase(TestCase):

    def test_command_add_users_to_campaign(self):
        # PREPARE DATA
        campaign = FakeCampaignFactory.create()
        filepath = './tests/campaign_users.csv'
        users = create_users_from_csv(filepath)

        # DO ACTION
        call_command('add_users_to_campaign', '-c', campaign.campaign_id, '-f', filepath)

        # ASSERTS
        for user in users:
            self.assertIn(user, campaign.users.all())
