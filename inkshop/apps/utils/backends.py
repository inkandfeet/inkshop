from django import forms
from clubhouse.models import StaffMember
from people.models import Person
from utils.encryption import lookup_hash, encrypt, decrypt, create_unique_hashid


class EncryptedEmailBackend(object):
    def authenticate(self, request, username=None, password=None):
        try:
            try:
                user = StaffMember.objects.get(hashed_email=lookup_hash(username))
                if user.check_password(password):
                    return user
            except StaffMember.DoesNotExist:
                user = Person.objects.get(hashed_email=lookup_hash(username))
                if user.check_password(password):
                    return user
        except:
            pass

        return None

    def get_user(self, user_id):
        try:
            return StaffMember.objects.get(pk=user_id)
        except StaffMember.DoesNotExist:
            return Person.objects.get(pk=user_id)
            return None
