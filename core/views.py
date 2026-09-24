from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json

from organizations.models import Organization, Note, TimelineEvent
from contacts.models import Contact
from research.models import Evidence, ResearchJob
from outreach.models import Outreach
from ai.services.next_action import NextActionEngine
from research.tasks import trigger_organization_research

@login_required
def dashboard_view(request):
    """The 'Today' View - Answers: 'What should I do right now?'"""
    organizations = Organization.objects.all()
    
    # Priority Counts
    followups_due = Outreach.objects.filter(status__in=[Outreach.Status.FOLLOWUP_DUE, Outreach.Status.AWAITING])
    ready_for_contact = Organization.objects.filter(status=Organization.Status.READY)
    needs_research = Organization.objects.filter(status=Organization.Status.DISCOVERED)
    contacted_count = Organization.objects.filter(status__in=[Organization.Status.CONTACTED, Organization.Status.AWAITING]).count()
    
    recently_found = organizations.order_by('-created_at')[:5]

    # Annotate organizations with Next Actions
    org_next_actions = []
    for org in organizations[:8]:
        next_act = NextActionEngine.get_next_action(org)
        org_next_actions.append({
            'org': org,
            'next_action': next_act
        })

    context = {
        'total_orgs': organizations.count(),
        'followups_due_count': followups_due.count(),
        'ready_for_contact_count': ready_for_contact.count(),
        'needs_research_count': needs_research.count(),
        'contacted_count': contacted_count,
        'followups_list': followups_due[:5],
        'ready_list': ready_for_contact[:5],
        'recently_found': recently_found,
        'org_next_actions': org_next_actions,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return redirect('core:dashboard')

    orgs = Organization.objects.filter(
        Q(name__icontains=query) |
        Q(industry__icontains=query) |
        Q(description__icontains=query) |
        Q(location__icontains=query)
    )
    
    contacts = Contact.objects.filter(
        Q(name__icontains=query) |
        Q(role__icontains=query) |
        Q(email__icontains=query)
    )
    
    evidence = Evidence.objects.filter(
        Q(claim__icontains=query) |
        Q(excerpt__icontains=query)
    )

    notes = Note.objects.filter(content__icontains=query)

    context = {
        'query': query,
        'orgs': orgs,
        'contacts': contacts,
        'evidence': evidence,
        'notes': notes,
    }
    return render(request, 'core/search.html', context)

@csrf_exempt
def api_capture_view(request):
    """API endpoint for Browser Extension / Bookmarklet capture: POST /api/v1/capture/"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    url = data.get('url', '').strip()
    title = data.get('title', '').strip()
    selected_text = data.get('selected_text', '').strip()
    org_name = data.get('organization_name', '').strip()

    if not url and not org_name:
        return JsonResponse({'error': 'URL or organization_name required'}, status=400)

    if not org_name and url:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        org_name = domain.replace('www.', '').split('.')[0].capitalize()

    org, created = Organization.objects.get_or_create(
        name=org_name,
        defaults={
            'website': url if '://' in url else f'https://{url}',
            'status': Organization.Status.DISCOVERED,
            'description': f"Captured via browser page: {title}"
        }
    )

    if selected_text:
        Note.objects.create(
            organization=org,
            content=f"Selected Text Captured: {selected_text}\nSource: {url}"
        )

    org.log_event("BROWSER_CAPTURED", f"Captured page '{title or url}' from browser extension.")
    trigger_organization_research(org)

    return JsonResponse({
        'success': True,
        'organization_id': org.id,
        'name': org.name,
        'created': created,
        'message': f"Saved {org.name} and enqueued research!"
    })
