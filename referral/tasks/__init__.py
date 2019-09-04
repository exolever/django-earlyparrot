from celery import current_app as app

from .campaign import CampaignSubscribeTask  # noqa

app.tasks.register(CampaignSubscribeTask())
