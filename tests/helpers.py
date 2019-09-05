from django.contrib.auth import get_user_model

from referral.faker_factories import faker


def normalize_email(email):
    """
    Normalize the email address by lowercasing the domain/email name part of it.
    """
    email = email or ''
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except ValueError:
        pass
    else:
        email = '@'.join([email_name.lower(), domain_part.lower()])
    return email


def create_users_from_csv(filepath, password='123456'):
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
