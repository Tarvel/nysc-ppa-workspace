from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    education = models.CharField(max_length=255, default="B.Sc. Computer Engineering")
    skills = models.TextField(
        default="Python, Django, FastAPI, PostgreSQL, Linux, Docker, REST APIs, Git, Systems Architecture",
        help_text="Comma separated list of core technical skills"
    )
    interests = models.TextField(
        default="Backend Engineering, IT Infrastructure, Information Management, Technical Support, Cloud Engineering",
        help_text="Primary technical interest areas"
    )
    preferred_locations = models.TextField(
        default="Abuja, Kwara, Lagos, Ibadan",
        help_text="Target NYSC PPA cities or states"
    )
    nysc_batch = models.CharField(max_length=100, default="2026 Batch A Stream 1", blank=True)
    nysc_state = models.CharField(max_length=100, default="FCT Abuja", blank=True)
    cv_summary = models.TextField(
        blank=True,
        default="Computer Engineering graduate with hands-on expertise building scalable Python/Django applications and managing backend infrastructure. Seeking NYSC PPA position in software development or IT management."
    )
    additional_context = models.TextField(blank=True, help_text="Any additional context for AI outreach generation")

    def __str__(self):
        return f"{self.user.username}'s PPA Profile"
