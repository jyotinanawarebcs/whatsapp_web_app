from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse


class CustomPaginator:
    """
    Custom pagination utility for consistent pagination across the application
    """
    
    @staticmethod
    def paginate_queryset(queryset, request, page_size=10, max_page_size=100):
        """
        Paginate a queryset with request parameters
        """
        try:
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', page_size))
            
            # Ensure valid values
            page = max(1, page)
            page_size = max(1, min(page_size, max_page_size))
            
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            return {
                'page_obj': page_obj,
                'paginator': paginator,
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'page_size': page_size
            }
            
        except (ValueError, EmptyPage, PageNotAnInteger) as e:
            # Return first page on error
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(1)
            
            return {
                'page_obj': page_obj,
                'paginator': paginator,
                'current_page': 1,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
                'page_size': page_size
            }


class PaginationResponse:
    """
    Standardized pagination response formatter
    """
    
    @staticmethod
    def create_response(data, pagination_info, **extra_fields):
        """
        Create standardized pagination response
        """
        response_data = {
            'contacts': data,  # 👈 'contacts' field use karo
            'pagination': {
                'current_page': pagination_info['current_page'],
                'total_pages': pagination_info['total_pages'],
                'total_items': pagination_info['total_items'],
                'has_next': pagination_info['has_next'],
                'has_previous': pagination_info['has_previous'],
                'page_size': pagination_info['page_size']
            },
            'status': 'success'
        }
        
        # Add any extra fields
        response_data.update(extra_fields)
        
        return JsonResponse(response_data)
    
    @staticmethod
    def create_error_response(error_message, status_code=500):
        """
        Create standardized error response
        """
        return JsonResponse({
            'error': error_message,
            'status': 'error'
        }, status=status_code)