from django.test import TestCase
from organizations.models import Organization
from contacts.models import Contact
from contacts.services.deduplicator import ContactDeduplicator
from contacts.services.contact_provider import MockContactProvider, extract_domain

class ContactTestCase(TestCase):
    def test_contact_deduplication(self):
        org = Organization.objects.create(name='Test Bank')
        c1 = Contact.objects.create(organization=org, name='Jane Doe', email='hr@testbank.com')
        c2 = Contact.objects.create(organization=org, name='Jane A. Doe', email='hr@testbank.com')
        
        duplicates = ContactDeduplicator.deduplicate(org)
        self.assertEqual(len(duplicates), 1)
        self.assertEqual(duplicates[0]['reason'], "Matching email address: hr@testbank.com")


class ContactProviderTestCase(TestCase):
    def test_mock_provider_returns_contacts(self):
        provider = MockContactProvider()
        contacts = provider.find_contacts("paystack.com")
        self.assertEqual(len(contacts), 2)
        self.assertEqual(contacts[0].email, "hr@paystack.com")
        self.assertEqual(contacts[1].email, "careers@paystack.com")
        self.assertEqual(contacts[0].verification_status, "Provider Sourced")

    def test_mock_provider_empty_domain(self):
        provider = MockContactProvider()
        contacts = provider.find_contacts("")
        self.assertEqual(len(contacts), 0)

    def test_extract_domain(self):
        self.assertEqual(extract_domain("https://www.paystack.com/about"), "paystack.com")
        self.assertEqual(extract_domain("http://google.com"), "google.com")
        self.assertEqual(extract_domain("https://careers.microsoft.com"), "careers.microsoft.com")
        self.assertEqual(extract_domain(""), "")
        self.assertEqual(extract_domain("paystack.com"), "paystack.com")

    def test_contact_provider_saves_to_db(self):
        org = Organization.objects.create(name='Paystack', website='https://paystack.com')
        provider = MockContactProvider()
        discovered = provider.find_contacts("paystack.com")
        for dc in discovered:
            Contact.objects.get_or_create(
                organization=org,
                email=dc.email,
                defaults={
                    'name': dc.name,
                    'role': dc.role,
                    'confidence': dc.confidence,
                    'verification_status': dc.verification_status,
                    'source': dc.source,
                }
            )
        self.assertEqual(Contact.objects.filter(organization=org).count(), 2)

        # Re-running should NOT create duplicates
        for dc in discovered:
            Contact.objects.get_or_create(
                organization=org,
                email=dc.email,
                defaults={'name': dc.name, 'role': dc.role, 'source': dc.source}
            )
        self.assertEqual(Contact.objects.filter(organization=org).count(), 2)

