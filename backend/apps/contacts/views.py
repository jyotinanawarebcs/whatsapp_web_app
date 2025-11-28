import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Contact
from .serializers import ContactSerializer
from .services.file_processing import process_uploaded_file
from .services.contact_service import ContactService
from apps.common.pagination import CustomPaginator, PaginationResponse


# -------------------------
# Upload contacts file API
# -------------------------
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def upload_contacts(request):
    if 'file' not in request.FILES:
        return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    filename = file.name
    file_ext = filename.split('.')[-1].lower()
    temp_path = f'/tmp/{filename}'

    # Save temporary file
    with open(temp_path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)
    
    try:
        result = process_uploaded_file(temp_path, filename, file_ext)
        return Response(result)
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': f'Processing failed: {str(e)}'}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# -------------------------
# CRUD APIs
# -------------------------
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_contact(request):
    serializer = ContactSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def retrieve_contact(request, pk):
    try:
        contact = Contact.objects.get(pk=pk)
    except Contact.DoesNotExist:
        return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ContactSerializer(contact)
    return Response(serializer.data)


@api_view(['PUT'])
# @permission_classes([IsAuthenticated])
def update_contact(request, pk):
    try:
        contact = Contact.objects.get(pk=pk)
    except Contact.DoesNotExist:
        return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ContactSerializer(contact, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
def delete_contact(request, pk):
    try:
        contact = Contact.objects.get(pk=pk)
    except Contact.DoesNotExist:
        return Response({'error': 'Contact not found'}, status=status.HTTP_404_NOT_FOUND)
    contact.delete()
    return Response({'success': True, 'id': pk})


# -------------------------
# File-based APIs
# -------------------------
@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def list_files(request):
    file_list = ContactService.get_file_list()
    return Response(file_list)


@api_view(['DELETE'])
# @permission_classes([IsAuthenticated])
def delete_by_file(request, filename):
    count = ContactService.delete_contacts_by_file(filename)
    return Response({'success': True, 'count': count})


# -------------------------
# Paginated APIs (using modular approach)
# -------------------------
@csrf_exempt
@require_http_methods(["GET"])
def list_contacts(request):
    """List all contacts with pagination"""
    try:
        # Get queryset using service
        queryset = ContactService.get_contact_queryset()
        
        # Paginate using custom paginator
        pagination_info = CustomPaginator.paginate_queryset(queryset, request)
        
        # Serialize data using service
        contacts_data = ContactService.serialize_contacts(pagination_info['page_obj'])
        
        # Return standardized response
        return PaginationResponse.create_response(contacts_data, pagination_info)
        
    except Exception as e:
        return PaginationResponse.create_error_response(str(e))


@csrf_exempt
@require_http_methods(["GET"])
def search_contacts(request):
    """Search contacts with pagination"""
    try:
        search_query = request.GET.get('search', '').strip()
        
        # Get filtered queryset using service
        queryset = ContactService.get_contact_queryset(search_query=search_query)
        
        # Paginate using custom paginator
        pagination_info = CustomPaginator.paginate_queryset(queryset, request)
        
        # Serialize data using service
        contacts_data = ContactService.serialize_contacts(pagination_info['page_obj'])
        
        # Return standardized response with search query
        return PaginationResponse.create_response(
            contacts_data, 
            pagination_info, 
            search_query=search_query
        )
        
    except Exception as e:
        return PaginationResponse.create_error_response(str(e))


@csrf_exempt
@require_http_methods(["GET"])
def contacts_by_file(request, filename):
    """Get contacts by filename with pagination"""
    try:
        # Get filtered queryset using service
        queryset = ContactService.get_contact_queryset(filename=filename)
        
        # Paginate using custom paginator
        pagination_info = CustomPaginator.paginate_queryset(queryset, request)
        
        # Serialize data using service
        contacts_data = ContactService.serialize_contacts(pagination_info['page_obj'])
        
        # Return standardized response with filename
        return PaginationResponse.create_response(
            contacts_data, 
            pagination_info, 
            filename=filename
        )
        
    except Exception as e:
        return PaginationResponse.create_error_response(str(e))