from django.test import TestCase
from organizations.models import Organization
from contacts.models import Contact
from contacts.services.deduplicator import ContactDeduplicator

class ContactTestCase(TestCase):
    def test_contact_deduplication(self):
        org = Organization.objects.create(name='Test Bank')
        c1 = Contact.objects.create(organization=org, name='Jane Doe', email='hr@testbank.com')
        c2 = Contact.objects.create(organization=org, name='Jane A. Doe', email='hr@testbank.com')
        
        duplicates = ContactDeduplicator.deduplicate(org)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]['reason'], "Matching email address: hr@testbank.com")
