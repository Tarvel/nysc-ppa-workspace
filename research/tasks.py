import os
from celery import shared_task
from django.utils import timezone
from organizations.models import Organization
from research.models import Source, Evidence, ResearchJob
from research.services.fetcher import WebPageFetcher
from research.services.search_provider import get_search_provider
from contacts.services.contact_provider import get_contact_provider, extract_domain
from contacts.models import Contact
from ai.services.brief_generator import BriefGenerator

@shared_task
def run_organization_research_task(organization_id: int, job_id: int = None):
    try:
        organization = Organization.objects.get(id=organization_id)
    except Organization.DoesNotExist:
        return False

    job = None
    if job_id:
        job = ResearchJob.objects.filter(id=job_id).first()
    if not job:
        job = ResearchJob.objects.create(organization=organization, status=ResearchJob.Status.RUNNING, started_at=timezone.now())
    else:
        job.status = ResearchJob.Status.RUNNING
        job.started_at = timezone.now()
        job.save()

    organization.status = Organization.Status.RESEARCHING
    organization.save()
    organization.log_event("RESEARCH_STARTED", f"Started research for {organization.name}")

    sources_fetched = []

    # 1. Fetch main website if exists
    if organization.website:
        job.progress = 20
        job.save()
        res = WebPageFetcher.fetch(organization.website)
        if res['success']:
            src, _ = Source.objects.get_or_create(
                organization=organization,
                url=res['url'],
                defaults={
                    'title': res['title'],
                    'domain': res['domain'],
                    'source_type': Source.SourceType.WEBSITE,
                    'content_excerpt': res['excerpt'],
                    'fetched_at': timezone.now()
                }
            )
            sources_fetched.append(src)

    # 2. Search web for company + careers + NYSC
    job.progress = 40
    job.save()
    search_provider = get_search_provider()
    search_results = search_provider.search(f"{organization.name} careers NYSC Abuja Nigeria", num_results=3)

    for item in search_results:
        src, created = Source.objects.get_or_create(
            organization=organization,
            url=item.url,
            defaults={
                'title': item.title,
                'domain': item.domain,
                'source_type': Source.SourceType.CAREERS if 'career' in item.url.lower() else Source.SourceType.DIRECTORY,
                'content_excerpt': item.snippet,
                'fetched_at': timezone.now()
            }
        )
        sources_fetched.append(src)

    # 3. Hunter.io HR contact discovery
    job.progress = 60
    job.save()
    domain = extract_domain(organization.website) if organization.website else ""
    if domain:
        try:
            contact_provider = get_contact_provider()
            discovered = contact_provider.find_contacts(domain)
            contacts_created = 0
            for dc in discovered:
                _, created = Contact.objects.get_or_create(
                    organization=organization,
                    email=dc.email,
                    defaults={
                        'name': dc.name,
                        'role': dc.role,
                        'phone': dc.phone,
                        'linkedin_url': dc.linkedin_url,
                        'confidence': dc.confidence,
                        'verification_status': dc.verification_status,
                        'source': dc.source,
                    }
                )
                if created:
                    contacts_created += 1
            if contacts_created:
                organization.log_event(
                    "HR_CONTACTS_DISCOVERED",
                    f"Found {contacts_created} HR contact(s) via {dc.source} for {domain}"
                )
        except Exception as e:
            print(f"Contact discovery error for {domain}: {e}")

    # 4. Process research via AI Brief Generator
    job.progress = 80
    job.save()
    
    BriefGenerator.process_organization_research(organization, sources_fetched)

    job.status = ResearchJob.Status.COMPLETED
    job.progress = 100
    job.completed_at = timezone.now()
    job.save()

    return True

def trigger_organization_research(organization: Organization):
    """Triggers research task asynchronously if Celery worker is running, else synchronously."""
    job = ResearchJob.objects.create(organization=organization, status=ResearchJob.Status.QUEUED)

    # On single-dyno deployments (e.g. Koyeb free tier) there is no
    # separate Celery worker.  Skip the broker round-trip and run inline.
    use_celery = os.getenv('CELERY_WORKER_RUNNING', '').lower() in ('1', 'true', 'yes')

    if use_celery:
        try:
            run_organization_research_task.delay(organization.id, job.id)
            return job
        except Exception as e:
            print(f"Celery dispatch failed: {e}. Executing synchronously...")

    # Synchronous fallback
    run_organization_research_task(organization.id, job.id)
    return job

