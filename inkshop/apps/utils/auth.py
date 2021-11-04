from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.views import PasswordResetView
from utils.encryption import lookup_hash


class InkshopPasswordResetForm(PasswordResetForm):

    def get_users(self, email):
        from people.models import Person
        active_users = Person.objects.filter(hashed_email=lookup_hash(email))
        return (u for u in active_users if u.has_usable_password())


class InkshopPasswordResetView(PasswordResetView):
    form_class = InkshopPasswordResetForm
