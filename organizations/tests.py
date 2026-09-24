from django.test import TestCase, Client
from django.contrib.auth.models import User
from organizations.models import Organization, Note, TimelineEvent
from outreach.models import Outreach
from contacts.models import Contact

class OrganizationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tai", password="taipassword")
        self.client = Client()
        self.client.login(username="tai", password="taipassword")

    def test_quick_add_organization(self):
        response = self.client.post('/organizations/quick-add/', {
            'name': 'Test Tech Corp',
            'website': 'https://testtech.com',
            'location': 'Abuja, Nigeria',
            'auto_research': 'false'
        })
        self.assertEqual(response.status_code, 302)
        org = Organization.objects.get(name='Test Tech Corp')
        self.assertEqual(org.website, 'https://testtech.com')
        # Research runs on creation, updating status to Ready to Contact
        self.assertIn(org.status, [Organization.Status.DISCOVERED, Organization.Status.READY, Organization.Status.RESEARCHING])

    def test_add_note_creates_timeline_event(self):
        org = Organization.objects.create(name='Test Corp')
        response = self.client.post(f'/organizations/{org.pk}/add-note/', {
            'content': 'Called HR today regarding PPA opening.'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Note.objects.filter(organization=org).count(), 1)
        self.assertTrue(TimelineEvent.objects.filter(organization=org, event_type='NOTE_ADDED').exists())
