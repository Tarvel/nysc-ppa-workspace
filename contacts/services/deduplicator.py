from contacts.models import Contact

class ContactDeduplicator:
    """Normalizes and deduplicates HR/recruitment contacts."""
    
    @staticmethod
    def deduplicate(organization) -> list:
        contacts = list(Contact.objects.filter(organization=organization))
        duplicates = []
        seen_emails = {}
        seen_names = {}

        for c in contacts:
            if c.email and c.email.lower() in seen_emails:
                duplicates.append({
                    'primary': seen_emails[c.email.lower()],
                    'duplicate': c,
                    'reason': f"Matching email address: {c.email}"
                })
            elif c.email:
                seen_emails[c.email.lower()] = c

            clean_name = c.name.lower().strip()
            if clean_name in seen_names and c not in [d['duplicate'] for d in duplicates]:
                duplicates.append({
                    'primary': seen_names[clean_name],
                    'duplicate': c,
                    'reason': f"Matching contact name: {c.name}"
                })
            else:
                seen_names[clean_name] = c

        return duplicates
