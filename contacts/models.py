from django.db import models
from organizations.models import Organization

class Contact(models.Model):
    class Confidence(models.TextChoices):
        HIGH = 'High', 'High'
        MEDIUM = 'Medium', 'Medium'
        LOW = 'Low', 'Low'

    class VerificationStatus(models.TextChoices):
        VERIFIED = 'Verified', 'Verified'
        PUBLICLY_LISTED = 'Publicly Listed', 'Publicly Listed'
        PROVIDER_SOURCED = 'Provider Sourced', 'Provider Sourced'
        UNVERIFIED = 'Unverified', 'Unverified'
        INVALID = 'Invalid', 'Invalid'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, blank=True, help_text="e.g. Talent Acquisition Manager, HR Lead")
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    linkedin_url = models.URLField(blank=True)
    source = models.CharField(max_length=255, default="Official Website", help_text="Where this contact was discovered")
    confidence = models.CharField(max_length=20, choices=Confidence.choices, default=Confidence.MEDIUM)
    verification_status = models.CharField(
        max_length=50,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PUBLICLY_LISTED
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.role or 'No Role'}) - {self.organization.name}"
