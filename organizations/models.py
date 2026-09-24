from django.db import models
from django.utils.text import slugify

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Organization(models.Model):
    class Status(models.TextChoices):
        DISCOVERED = 'Discovered', 'Discovered'
        RESEARCHING = 'Researching', 'Researching'
        READY = 'Ready to Contact', 'Ready to Contact'
        CONTACTED = 'Contacted', 'Contacted'
        AWAITING = 'Awaiting Response', 'Awaiting Response'
        FOLLOWUP = 'Follow Up Due', 'Follow Up Due'
        DISCUSSION = 'In Discussion', 'In Discussion'
        POSITIVE = 'Positive', 'Positive'
        DECLINED = 'Declined', 'Declined'
        NO_RESPONSE = 'No Response', 'No Response'
        CLOSED = 'Closed', 'Closed'

    class Priority(models.TextChoices):
        LOW = 'Low', 'Low'
        NORMAL = 'Normal', 'Normal'
        HIGH = 'High', 'High'

    name = models.CharField(max_length=255)
    legal_name = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    industry = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True, help_text="e.g. Abuja, Nigeria")
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    general_email = models.EmailField(blank=True)
    careers_url = models.URLField(blank=True)

    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.DISCOVERED
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL
    )

    tags = models.ManyToManyField(Tag, blank=True, related_name='organizations')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    def log_event(self, event_type, description, metadata=None):
        TimelineEvent.objects.create(
            organization=self,
            event_type=event_type,
            description=description,
            metadata=metadata or {}
        )

class Opportunity(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='opportunities')
    title = models.CharField(max_length=255)
    opportunity_type = models.CharField(max_length=100, default="PPA Inquiry", help_text="e.g. NYSC PPA, Internship, IT Support")
    department = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    source_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.organization.name}"

class Note(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on {self.organization.name} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class TimelineEvent(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='timeline_events')
    event_type = models.CharField(max_length=50)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.event_type}] {self.organization.name} - {self.description[:30]}"
