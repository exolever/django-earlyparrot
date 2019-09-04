#!/usr/bin/env python
# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

from celery import Celery


def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'

    app = Celery('referral')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.autodiscover_tasks()
    app.conf.update(BROKER_URL='redis://localhost:6379/0')

    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(test_args)
    sys.exit(bool(failures))


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
