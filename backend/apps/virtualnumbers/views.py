from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services.numbers_service import numbers_service
from .serializers import (
    UpdateBusinessNumberSerializer,
    CreateVirtualNumberSerializer,
    UpdateVirtualNumberSerializer,
    ManualSwitchSerializer
)
import logging

logger = logging.getLogger(__name__)

# ==================================================
# GET BUSINESS NUMBER
# ==================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_business_number(request):
    """
    Get the primary business number configuration
    Endpoint: GET /api/admin/business-number
    """
    try:
        business_number = numbers_service.get_business_number()
        if business_number:
            return Response({
                'id': business_number.id,
                'business_name': business_number.business_name,
                'waba_id': business_number.waba_id,
                'phone_number_id': business_number.phone_number_id,
                'display_phone_number': business_number.display_phone_number,
                'auto_switch_enabled': business_number.auto_switch_enabled
            }, status=status.HTTP_200_OK)
        return Response({'message': 'No business number configured'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error getting business number: {str(e)}")
        return Response({'error': 'Failed to get business number'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==================================================
# UPDATE BUSINESS NUMBER
# ==================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_business_number(request):
    """
    Create or update business number configuration
    Endpoint: PUT /api/admin/business-number
    """
    try:
        serializer = UpdateBusinessNumberSerializer(data=request.data)
        if serializer.is_valid():
            business_number = numbers_service.upsert_business_number(serializer.validated_data)
            return Response({
                'id': business_number.id,
                'business_name': business_number.business_name,
                'message': 'Business number updated successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error updating business number: {str(e)}")
        return Response({'error': 'Failed to update business number'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==================================================
# LIST VIRTUAL NUMBERS
# ==================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_virtual_numbers(request):
    """
    Get all virtual numbers with sorting
    Endpoint: GET /api/admin/virtual-numbers
    """
    try:
        virtual_numbers = numbers_service.list_virtual_numbers()
        numbers_list = []
        for number in virtual_numbers:
            numbers_list.append({
                'id': number.id,
                'phone_number_id': number.phone_number_id,
                'status': number.status,
                'quality_rating': number.quality_rating,
                'is_primary': number.is_primary,
                'message_count_24h': number.message_count_24h,
                'last_used_at': number.last_used_at,
                'business_number_id': number.business_number_id
            })
        return Response(numbers_list, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error listing virtual numbers: {str(e)}")
        return Response({'error': 'Failed to list virtual numbers'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==================================================
# CREATE VIRTUAL NUMBER
# ==================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_virtual_number(request):
    """
    Create a new virtual number
    Endpoint: POST /api/admin/virtual-numbers
    """
    try:
        serializer = CreateVirtualNumberSerializer(data=request.data)
        if serializer.is_valid():
            virtual_number = numbers_service.create_virtual_number(serializer.validated_data)
            return Response({
                'id': virtual_number.id,
                'phone_number_id': virtual_number.phone_number_id,
                'status': virtual_number.status,
                'message': 'Virtual number created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating virtual number: {str(e)}")
        return Response({'error': 'Failed to create virtual number'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ==================================================
# UPDATE VIRTUAL NUMBER
# ==================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_virtual_number(request, id):
    """
    Update an existing virtual number
    Endpoint: PUT /api/admin/virtual-numbers/{id}
    """
    try:
        serializer = UpdateVirtualNumberSerializer(data=request.data)
        if serializer.is_valid():
            virtual_number = numbers_service.update_virtual_number(id, serializer.validated_data)
            return Response({
                'id': virtual_number.id,
                'phone_number_id': virtual_number.phone_number_id,
                'status': virtual_number.status,
                'message': 'Virtual number updated successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error updating virtual number {id}: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ==================================================
# MANUAL SWITCH VIRTUAL NUMBER
# ==================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def manual_switch(request):
    """
    Manually switch to a specific virtual number or auto-select one
    Endpoint: PUT /api/admin/virtual-numbers/switch
    """
    try:
        serializer = ManualSwitchSerializer(data=request.data)
        if serializer.is_valid():
            target_id = serializer.validated_data.get('target_id')
            virtual_number = numbers_service.manual_switch(target_id)
            return Response({
                'id': virtual_number.id,
                'phone_number_id': virtual_number.phone_number_id,
                'status': virtual_number.status,
                'message': 'Virtual number switched successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error in manual switch: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)