from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.test import TestCase

from unittest.mock import patch

from referral.faker_factories import FakeCampaignFactory, faker
from referral.helpers import normalize_email


class CampaignTestCase(TestCase):

    @patch('referral.tasks.subscriber.SubscriberGetTokenTask.apply_async')
    def test_get_token_from_earlyparrot_after_add_user(self, patch_get_token_task):
        # PREPARE DATA
        campaign = FakeCampaignFactory(
            campaign_id='5d63bef606b0367560f6b9be'
        )

        user = get_user_model().objects.create(
            username=faker.user_name(),
            email=faker.email(),
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            is_superuser=False,
            is_active=True,
        )

        # DO ACTION
        campaign.add_subscriber(user)

        # ASSERTIONS
        self.assertTrue(campaign.users.count(), 1)
        self.assertTrue(patch_get_token_task.called)
