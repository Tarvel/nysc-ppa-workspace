from django.db import models
from organizations.models import Organization

class Source(models.Model):
    class SourceType(models.TextChoices):
        WEBSITE = 'Website', 'Website'
        CAREERS = 'Careers Page', 'Careers Page'
        LINKEDIN = 'LinkedIn', 'LinkedIn'
        NEWS = 'News Article', 'News Article'
        JOB_LISTING = 'Job Listing', 'Job Listing'
        DIRECTORY = 'Public Directory', 'Public Directory'
        USER_PASTED = 'User Input', 'User Input'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='sources')
    url = models.URLField(max_length=500)
    title = models.CharField(max_length=255, blank=True)
    domain = models.CharField(max_length=150, blank=True)
    source_type = models.CharField(max_length=50, choices=SourceType.choices, default=SourceType.WEBSITE)
    content_excerpt = models.TextField(blank=True)
    discovered_at = models.DateTimeField(auto_now_add=True)
    fetched_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.source_type}: {self.title or self.domain or self.url}"

class Evidence(models.Model):
    class Confidence(models.TextChoices):
        HIGH = 'High', 'High'
        MEDIUM = 'Medium', 'Medium'
        LOW = 'Low', 'Low'
        UNKNOWN = 'Unknown', 'Unknown'

    class EvidenceType(models.TextChoices):
        NYSC_ACCEPTANCE = 'NYSC Acceptance Evidence', 'NYSC Acceptance Evidence'
        TECHNICAL_ROLES = 'Technical Department/Roles', 'Technical Department/Roles'
        GRADUATE_RECRUITMENT = 'Graduate Recruitment Program', 'Graduate Recruitment Program'
        LOCATION_PRESENCE = 'Target Location Presence', 'Target Location Presence'
        CAREERS_CONTACT = 'Direct Careers Contact', 'Direct Careers Contact'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='evidence_items')
    source = models.ForeignKey(Source, on_delete=models.SET_NULL, null=True, blank=True, related_name='evidence')
    claim = models.TextField(help_text="What this evidence claims")
    evidence_type = models.CharField(max_length=50, choices=EvidenceType.choices, default=EvidenceType.TECHNICAL_ROLES)
    excerpt = models.TextField(blank=True, help_text="Exact excerpt or snippet from source")
    confidence = models.CharField(max_length=20, choices=Confidence.choices, default=Confidence.MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidence ({self.confidence}): {self.claim[:40]}"

class ResearchJob(models.Model):
    class Status(models.TextChoices):
        QUEUED = 'Queued', 'Queued'
        RUNNING = 'Running', 'Running'
        COMPLETED = 'Completed', 'Completed'
        PARTIAL = 'Partially Completed', 'Partially Completed'
        FAILED = 'Failed', 'Failed'

    class Depth(models.TextChoices):
        QUICK = 'Quick', 'Quick'
        STANDARD = 'Standard', 'Standard'
        DEEP = 'Deep', 'Deep'

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='research_jobs')
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.QUEUED)
    depth = models.CharField(max_length=20, choices=Depth.choices, default=Depth.STANDARD)
    progress = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ResearchJob #{self.id} for {self.organization.name} [{self.status}]"
