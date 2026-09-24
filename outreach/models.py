from django.db import models
from organizations.models import Organization
from contacts.models import Contact

class Outreach(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'Draft', 'Draft'
        READY = 'Ready', 'Ready'
        SENT = 'Sent', 'Sent'
        AWAITING = 'Awaiting Response', 'Awaiting Response'
        FOLLOWUP_DUE = 'Follow-up Due', 'Follow-up Due'
        RESPONDED = 'Responded', 'Responded'
        POSITIVE = 'Positive', 'Positive'
        DECLINED = 'Declined', 'Declined'
        CLOSED = 'Closed', 'Closed'

    class Channel(models.TextChoices):
        EMAIL = 'Email', 'Email'
        LINKEDIN = 'LinkedIn', 'LinkedIn'
        PHONE = 'Phone Call', 'Phone Call'
        IN_PERSON = 'In-Person / Camp', 'In-Person / Camp'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='outreaches')
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name='outreaches')
    channel = models.CharField(max_length=50, choices=Channel.choices, default=Channel.EMAIL)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.DRAFT)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    follow_up_at = models.DateTimeField(null=True, blank=True)
    response = models.TextField(blank=True, help_text="Notes or exact response received from organization")
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Outreach to {self.organization.name} [{self.status}]"
