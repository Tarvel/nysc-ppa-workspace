from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Organization, Note, TimelineEvent, Tag
from contacts.models import Contact
from contacts.services.deduplicator import ContactDeduplicator
from research.models import Source, Evidence, ResearchJob
from outreach.models import Outreach
from ai.services.next_action import NextActionEngine
from research.tasks import trigger_organization_research

@login_required
def organization_list_view(request):
    status_filter = request.GET.get('status', 'ALL')
    search_q = request.GET.get('q', '').strip()

    orgs = Organization.objects.all()

    if status_filter != 'ALL':
        orgs = orgs.filter(status=status_filter)

    if search_q:
        orgs = orgs.filter(
            Q(name__icontains=search_q) |
            Q(industry__icontains=search_q) |
            Q(location__icontains=search_q)
        )

    context = {
        'organizations': orgs,
        'selected_status': status_filter,
        'search_q': search_q,
        'statuses': Organization.Status.choices,
    }
    return render(request, 'organizations/list.html', context)

@login_required
def organization_detail_view(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    
    contacts = org.contacts.all()
    duplicates = ContactDeduplicator.deduplicate(org)
    sources = org.sources.all()
    evidence_items = org.evidence_items.all()
    notes = org.notes.all()
    timeline_events = org.timeline_events.all()
    outreaches = org.outreaches.all()
    
    next_action = NextActionEngine.get_next_action(org)

    context = {
        'org': org,
        'contacts': contacts,
        'duplicates': duplicates,
        'sources': sources,
        'evidence_items': evidence_items,
        'notes': notes,
        'timeline_events': timeline_events,
        'outreaches': outreaches,
        'next_action': next_action,
    }
    return render(request, 'organizations/detail.html', context)

@login_required
def quick_add_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        website = request.POST.get('website', '').strip()
        location = request.POST.get('location', 'Abuja, Nigeria').strip()
        auto_research = request.POST.get('auto_research') == 'true'

        if not name:
            messages.error(request, "Organization name is required.")
            return redirect('core:dashboard')

        org, created = Organization.objects.get_or_create(
            name=name,
            defaults={
                'website': website,
                'location': location,
                'status': Organization.Status.DISCOVERED
            }
        )

        org.log_event("ADDED", f"Organization {name} created via quick capture.")

        if auto_research or created:
            trigger_organization_research(org)
            messages.success(request, f"Captured {name}! Background research has been started.")
        else:
            messages.info(request, f"{name} saved.")

        return redirect('organizations:detail', pk=org.pk)

    return redirect('core:dashboard')

@login_required
def add_note_view(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Note.objects.create(organization=org, content=content)
            org.log_event("NOTE_ADDED", f"Added note: '{content[:40]}...'")
            messages.success(request, "Note added to organization timeline.")
    return redirect('organizations:detail', pk=org.pk)

@login_required
def trigger_research_view(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    trigger_organization_research(org)
    messages.success(request, f"Started background research for {org.name}.")
    return redirect('organizations:detail', pk=org.pk)

@login_required
def update_status_view(request, pk):
    org = get_object_or_404(Organization, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Organization.Status.choices):
            old_status = org.status
            org.status = new_status
            org.save()
            org.log_event("STATUS_CHANGE", f"Status updated from '{old_status}' to '{new_status}'.")
            messages.success(request, f"Status updated to {new_status}.")
    return redirect('organizations:detail', pk=org.pk)
