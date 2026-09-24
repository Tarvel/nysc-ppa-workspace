from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from organizations.models import Organization
from .models import Contact

@login_required
def create_contact_view(request, org_id):
    org = get_object_or_404(Organization, pk=org_id)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        role = request.POST.get('role', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        linkedin_url = request.POST.get('linkedin_url', '').strip()
        confidence = request.POST.get('confidence', 'Medium')

        if name:
            contact = Contact.objects.create(
                organization=org,
                name=name,
                role=role,
                email=email,
                phone=phone,
                linkedin_url=linkedin_url,
                confidence=confidence,
                verification_status=Contact.VerificationStatus.PUBLICLY_LISTED,
                source="User Input"
            )
            org.log_event("CONTACT_ADDED", f"Added contact: {name} ({role or 'No role'})")
            messages.success(request, f"Added contact {name}.")
    return redirect('organizations:detail', pk=org.pk)

@login_required
def delete_contact_view(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    org_pk = contact.organization.pk
    contact.delete()
    messages.success(request, "Contact removed.")
    return redirect('organizations:detail', pk=org_pk)
