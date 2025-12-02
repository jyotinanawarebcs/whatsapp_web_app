from django.db.models import Q
from ..models import Contact


class ContactService:
    """
    Service layer for contact-related operations
    """
    
    @staticmethod
    def get_contact_queryset(search_query=None, filename=None):
        """
        Get filtered contact queryset
        """
        queryset = Contact.objects.all().order_by('-id')
        
        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(phone__icontains=search_query) |
                Q(name__icontains=search_query) |
                Q(source_file__icontains=search_query)
            )
        
        # Apply filename filter
        if filename:
            queryset = queryset.filter(source_file=filename)
            
        return queryset
    
    @staticmethod
    def serialize_contact(contact):
        """
        Serialize single contact
        """
        return {
            'id': contact.id,
            'name': contact.name,
            'phone': contact.phone,
            'source_file': contact.source_file,
            'is_active': contact.is_active,
            'created_at': contact.created_at.isoformat() if contact.created_at else None,
        }
    
    @staticmethod
    def serialize_contacts(contacts):
        """
        Serialize multiple contacts
        """
        return [ContactService.serialize_contact(contact) for contact in contacts]
    
    @staticmethod
    def get_file_list():
        """
        Get list of all source files with counts
        """
        files = Contact.objects.exclude(source_file__isnull=True) \
            .values('source_file').distinct()

        file_list = [
            {
                'filename': f['source_file'],
                'count': Contact.objects.filter(source_file=f['source_file']).count()
            }
            for f in files
        ]
        
        return file_list
    
    @staticmethod
    def delete_contacts_by_file(filename):
        """
        Delete all contacts by filename
        """
        count = Contact.objects.filter(source_file=filename).count()
        Contact.objects.filter(source_file=filename).delete()
        return count