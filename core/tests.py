import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from organizations.models import Organization, Note

class CoreTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tai", password="taipassword")
        self.client = Client()

    def test_browser_capture_api(self):
        payload = {
            'url': 'https://mainone.net/careers',
            'title': 'MainOne Careers',
            'selected_text': 'We recruit NYSC corps members for network & software engineering in Abuja.',
            'organization_name': 'MainOne'
        }
        response = self.client.post('/api/v1/capture/', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        
        org = Organization.objects.get(name='MainOne')
        self.assertTrue(Note.objects.filter(organization=org).exists())
