from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = "Creates initial single user account for Tai"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(username="tai", defaults={"email": "tai@example.com", "first_name": "Tai"})
        if created:
            user.set_password("taipassword")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created user 'tai' with password 'taipassword'"))
        else:
            self.stdout.write(self.style.SUCCESS("User 'tai' already exists."))
        
        profile, p_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                "education": "B.Sc. Computer Engineering",
                "skills": "Python, Django, FastAPI, PostgreSQL, Linux, Docker, REST APIs, Git",
                "interests": "Backend Engineering, IT Infrastructure, Information Management, Systems Architecture",
                "preferred_locations": "Abuja, Kwara, Ibadan, Lagos",
                "nysc_batch": "2026 Batch A Stream 1",
                "nysc_state": "FCT Abuja",
                "cv_summary": "Computer Engineering graduate with hands-on expertise building scalable backend applications and managing IT infrastructure. Seeking NYSC PPA placement."
            }
        )
        if p_created:
            self.stdout.write(self.style.SUCCESS("Created default UserProfile for Tai"))
