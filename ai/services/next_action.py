from organizations.models import Organization

class NextActionEngine:
    """Computes the 1 most logical next action for an organization with clear explainability."""
    
    @staticmethod
    def get_next_action(organization: Organization) -> dict:
        status = organization.status
        contacts_count = organization.contacts.count()
        sources_count = organization.sources.count()
        outreaches = organization.outreaches.all()
        has_outreach = outreaches.exists()

        if status == Organization.Status.DISCOVERED:
            return {
                'action': 'Run background research',
                'why': 'This organization was newly added and needs web research to discover careers, locations, and contacts.',
                'button_text': 'Start Research',
                'action_type': 'RESEARCH'
            }

        if status == Organization.Status.RESEARCHING:
            return {
                'action': 'Awaiting research completion',
                'why': 'Background web research is currently fetching pages and extracting evidence.',
                'button_text': 'View Progress',
                'action_type': 'VIEW'
            }

        if contacts_count == 0:
            return {
                'action': 'Find HR / Careers Contact',
                'why': 'Research is complete, but no verified recruitment or careers contact has been found yet.',
                'button_text': 'Find Contacts',
                'action_type': 'CONTACT'
            }

        if not has_outreach:
            return {
                'action': 'Draft Outreach Message',
                'why': f'You have research and contact info for {organization.name}, but have not prepared an inquiry email yet.',
                'button_text': 'Prepare Outreach',
                'action_type': 'OUTREACH'
            }

        latest_outreach = outreaches.first()
        if latest_outreach.status in ['Draft', 'Ready']:
            return {
                'action': 'Review and Send Outreach Email',
                'why': 'An outreach draft is prepared. Review it, copy or send, and mark as sent.',
                'button_text': 'Review Draft',
                'action_type': 'REVIEW_OUTREACH'
            }

        if status == Organization.Status.FOLLOWUP:
            return {
                'action': 'Send Follow-up Message',
                'why': 'Follow-up period reached with no reply. Send a polite reminder.',
                'button_text': 'Draft Follow-up',
                'action_type': 'FOLLOWUP'
            }

        if status == Organization.Status.AWAITING:
            return {
                'action': 'Awaiting Organization Response',
                'why': f'Outreach sent on {latest_outreach.sent_at.strftime("%b %d") if latest_outreach.sent_at else "recently"}. Check email or snooze follow-up.',
                'button_text': 'Log Response',
                'action_type': 'RESPONSE'
            }

        return {
            'action': f'Status: {status}',
            'why': 'Review current notes and timeline.',
            'button_text': 'View Timeline',
            'action_type': 'TIMELINE'
        }
