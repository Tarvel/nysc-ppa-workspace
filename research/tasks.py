import os
from celery import shared_task
from django.utils import timezone
from organizations.models import Organization
from research.models import Source, Evidence, ResearchJob
from research.services.fetcher import WebPageFetcher
from research.services.search_provider import get_search_provider
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
    job.progress = 50
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

    # 3. Process research via AI Brief Generator
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

