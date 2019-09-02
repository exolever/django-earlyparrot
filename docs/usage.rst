=====
Usage
=====

To use django-earlyparrot in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'referral.apps.TypeformFeedbackConfig',
        ...
    )

Add django-earlyparrot's URL patterns:

.. code-block:: python

    from referral import urls as referral_urls


    urlpatterns = [
        ...
        url(r'^', include(referral_urls)),
        ...
    ]
