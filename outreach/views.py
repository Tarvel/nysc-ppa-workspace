from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import urllib.parse

from organizations.models import Organization
from contacts.models import Contact
from accounts.models import UserProfile
from .models import Outreach
from ai.services.outreach_drafter import OutreachDrafter

@login_required
def outreach_list_view(request):
    status_filter = request.GET.get('status', 'ALL')
    outreaches = Outreach.objects.all()

    if status_filter != 'ALL':
        outreaches = outreaches.filter(status=status_filter)

    context = {
        'outreaches': outreaches,
        'selected_status': status_filter,
        'statuses': Outreach.Status.choices,
    }
    return render(request, 'outreach/list.html', context)

@login_required
def prepare_outreach_view(request, org_id):
    org = get_object_or_404(Organization, pk=org_id)
    contacts = org.contacts.all()
    selected_contact_id = request.GET.get('contact_id')
    contact = None
    if selected_contact_id:
        contact = contacts.filter(pk=selected_contact_id).first()
    if not contact:
        contact = contacts.first()

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        contact_id = request.POST.get('contact_id')
        action = request.POST.get('action', 'save_draft')

        c_obj = Contact.objects.filter(pk=contact_id).first() if contact_id else contact

        outreach = Outreach.objects.create(
            organization=org,
            contact=c_obj,
            subject=subject,
            message=message,
            status=Outreach.Status.SENT if action == 'mark_sent' else Outreach.Status.DRAFT,
            sent_at=timezone.now() if action == 'mark_sent' else None,
            follow_up_at=timezone.now() + timedelta(days=5) if action == 'mark_sent' else None
        )

        if action == 'mark_sent':
            org.status = Organization.Status.AWAITING
            org.save()
            org.log_event("EMAIL_SENT", f"Outreach sent to {c_obj.name if c_obj else org.name}. Follow-up set for 5 days.")
            messages.success(request, f"Outreach logged as sent! Follow-up reminder set for {outreach.follow_up_at.strftime('%b %d')}.")
        else:
            org.log_event("OUTREACH_DRAFTED", f"Drafted outreach for {org.name}.")
            messages.success(request, "Outreach draft saved.")

        return redirect('organizations:detail', pk=org.pk)

    # Generate AI initial draft
    draft_data = OutreachDrafter.draft_initial_outreach(org, contact, profile)
    
    # Pre-build mailto URL
    recipient_email = contact.email if (contact and contact.email) else org.general_email
    mailto_url = ""
    if recipient_email:
        mailto_url = f"mailto:{recipient_email}?subject={urllib.parse.quote(draft_data['subject'])}&body={urllib.parse.quote(draft_data['message'])}"

    context = {
        'org': org,
        'contacts': contacts,
        'selected_contact': contact,
        'draft_subject': draft_data['subject'],
        'draft_message': draft_data['message'],
        'mailto_url': mailto_url,
    }
    return render(request, 'outreach/prepare.html', context)

@login_required
def update_outreach_status_view(request, pk):
    outreach = get_object_or_404(Outreach, pk=pk)
    org = outreach.organization
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        response_notes = request.POST.get('response', '').strip()
        
        if new_status:
            outreach.status = new_status
            if response_notes:
                outreach.response = response_notes
            outreach.save()

            if new_status == Outreach.Status.SENT:
                outreach.sent_at = timezone.now()
                outreach.follow_up_at = timezone.now() + timedelta(days=5)
                outreach.save()
                org.status = Organization.Status.AWAITING
                org.save()
                org.log_event("EMAIL_SENT", f"Outreach marked as sent.")
            elif new_status in [Outreach.Status.POSITIVE, Outreach.Status.RESPONDED]:
                org.status = Organization.Status.POSITIVE if new_status == Outreach.Status.POSITIVE else Organization.Status.DISCUSSION
                org.save()
                org.log_event("RESPONSE_RECEIVED", f"Response recorded: {new_status}. Notes: {response_notes[:40]}")
            elif new_status in [Outreach.Status.DECLINED, Outreach.Status.CLOSED]:
                org.status = Organization.Status.DECLINED if new_status == Outreach.Status.DECLINED else Organization.Status.CLOSED
                org.save()
                org.log_event("OUTREACH_CLOSED", f"Outreach status updated to {new_status}.")

            messages.success(request, f"Updated outreach status to {new_status}.")

    return redirect('organizations:detail', pk=org.pk)
