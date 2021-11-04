import logging
import json
from utils.helpers import reverse
from django.core import mail
from django.conf import settings

from django.test.utils import override_settings

from archives.models import HistoricalEvent
from people.models import Person
from inkmail.models import Subscription, OutgoingMessage
from inkmail.tasks import process_outgoing_message_queue
from utils.factory import Factory
from utils.test_helpers import MockRequestsTestCase, MailTestCase
from utils.encryption import normalize_lower_and_encrypt, normalize_and_encrypt, encrypt, decrypt
import mock
import unittest


class TestRenderingBasics(MailTestCase):

    def setUp(self, *args, **kwargs):
        self.newsletter = Factory.newsletter()
        super(TestRenderingBasics, self).setUp(*args, **kwargs)

    def test_unsubscribe_link_included_in_every_newsletter_message_send(self):
        self.assertEquals(len(mail.outbox), 0)
        self.create_subscribed_person()
        self.send_newsletter_message(message_body="""Hey FirstName,

Congrats on your purchase of the 7-Day Sprint, and welcome to the community of sprinters!

This course has been a labor of love, and helped me and lots of folks get unstuck,
finish things off, and just get moving.  I hope it does the same for you.

If you ever have any questions or comments, you can email me directly anytime at me@example.com

-Steven


Here's everything you need to know about your purchase.

**Accessing the course:**
1. Go to https://courses.inkandfeet.com/course-name
2. Log in with the email and password you created when you purchased.
3. Enjoy!


**Forgot your password?**

Just go to the page above, and use the "Forgot Password" link - it'll walk you through resetting.


**Need a receipt?**

You'll have another email in your inbox, right next to this one from Stripe, my billing provider.
That's your official receipt.


**Want a refund?**

Just log in, go to account, and click refund from your list of purchases.

Have a great day, and I hope you enjoy the course!
        """)

        self.assertEquals(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEquals(OutgoingMessage.objects.count(), 1)
        om = OutgoingMessage.objects.all()[0]
        self.assertIn(om.unsubscribe_link, m.body)
        self.assertIn('href="%s"' % (om.unsubscribe_link, ), m.alternatives[0][0])
        self.assertIn('<ol>', m.alternatives[0][0])
