from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction
from .services.campaign_service import campaign_service
from .serializers import (
    CreateCampaignSerializer, 
    UpdateCampaignSerializer, 
    RunCampaignSerializer
)
import logging

logger = logging.getLogger(__name__)

# ==================================================
# CREATE NEW CAMPAIGN
# ==================================================
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def create_campaign(request):
    """
    Create new campaign - POST /api/campaigns/create
    """
    try:
        serializer = CreateCampaignSerializer(data=request.data)
        if serializer.is_valid():
            campaign = campaign_service.create(serializer.validated_data, request.user)
            return Response({
                'id': campaign.id,
                'campaign_name': campaign.campaign_name,
                'status': campaign.status,
                'message': 'Campaign created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        return Response(
            {'error': 'Failed to create campaign'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ==================================================
# RUN CAMPAIGN
# ==================================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_campaign(request):
    """
    Run existing campaign - POST /api/campaigns/run
    """
    try:
        serializer = RunCampaignSerializer(data=request.data)
        if serializer.is_valid():
            result = campaign_service.run_campaign(serializer.validated_data, request.user)
            return Response({
                'campaign_id': result['campaign'].id,
                'assigned_number': result['assigned_number'],
                'dispatch': result['dispatch'],
                'message': 'Campaign started successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error running campaign: {str(e)}")
        return Response(
            {'error': 'Failed to run campaign'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ==================================================
# GET ALL CAMPAIGNS
# ==================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_campaigns(request):
    """
    Get all campaigns for user - GET /api/campaigns/
    """
    try:
        campaigns = campaign_service.find_all(request.user.id)
        campaign_list = []
        for campaign in campaigns:
            campaign_list.append({
                'id': campaign.id,
                'campaign_name': campaign.campaign_name,
                'status': campaign.status,
                'recipients_count': campaign.recipients_count,
                'sent_count': campaign.sent_count,
                'success_count': campaign.success_count,
                'failed_count': campaign.failed_count,
                'read_count': campaign.read_count,
                'created_at': campaign.created_at,
                'updated_at': campaign.updated_at
            })
        return Response(campaign_list, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching campaigns: {str(e)}")
        return Response(
            {'error': 'Failed to fetch campaigns'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ==================================================
# GET ACTIVE CAMPAIGNS
# ==================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_campaigns(request):
    """
    Get active campaigns - GET /api/campaigns/active-campaigns
    """
    try:
        campaigns = campaign_service.find_all(request.user.id)
        active_campaigns = [campaign for campaign in campaigns if campaign.status == 'active']
        
        campaign_list = []
        for campaign in active_campaigns:
            progress = (campaign.sent_count / campaign.recipients_count * 100) if campaign.recipients_count > 0 else 0
            campaign_list.append({
                'id': campaign.id,
                'campaign_name': campaign.campaign_name,
                'status': campaign.status,
                'recipients_count': campaign.recipients_count,
                'sent_count': campaign.sent_count,
                'success_count': campaign.success_count,
                'progress': round(progress, 2),
                'created_at': campaign.created_at
            })
        return Response(campaign_list, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching active campaigns: {str(e)}")
        return Response(
            {'error': 'Failed to fetch active campaigns'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ==================================================
# GET DASHBOARD STATS
# ==================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_dashboard_stats(request):
    """
    Get dashboard statistics - GET /api/campaigns/stats
    """
    try:
        stats = campaign_service.get_dashboard_stats(request.user.id)
        return Response(stats, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        return Response(
            {'error': 'Failed to fetch dashboard stats'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ==================================================
# GET RECENT CAMPAIGNS
# ==================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recent_campaigns(request):
    """
    Get recent campaigns - GET /api/campaigns/recent
    """
    try:
        limit = request.GET.get('limit', '4')
        try:
            limit = int(limit)
            if limit <= 0:
                limit = 4
        except ValueError:
            limit = 4
        
        campaigns = campaign_service.get_recent(request.user.id, limit)
        campaign_list = []
        for campaign in campaigns:
            campaign_list.append({
                'id': campaign.id,
                'campaign_name': campaign.campaign_name,
                'status': campaign.status,
                'sent_count': campaign.sent_count,
                'recipients_count': campaign.recipients_count,
                'created_at': campaign.created_at
            })
        return Response(campaign_list, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching recent campaigns: {str(e)}")
        return Response(
            {'error': 'Failed to fetch recent campaigns'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ==================================================
# GET SINGLE CAMPAIGN
# ==================================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_campaign(request, id):
    """
    Get single campaign by ID - GET /api/campaigns/{id}
    """
    try:
        campaign = campaign_service.find_one(id)
        campaign_data = {
            'id': campaign.id,
            'campaign_name': campaign.campaign_name,
            'name': campaign.name,
            'template_id': campaign.template_id,
            'status': campaign.status,
            'caption': campaign.caption,
            'media_url': campaign.media_url,
            'media_type': campaign.media_type,
            'media_name': campaign.media_name,
            'attachment_url': campaign.attachment_url,
            'cta_buttons': campaign.cta_buttons,
            'scheduled_start': campaign.scheduled_start,
            'scheduled_end': campaign.scheduled_end,
            'recipients_count': campaign.recipients_count,
            'sent_count': campaign.sent_count,
            'success_count': campaign.success_count,
            'failed_count': campaign.failed_count,
            'read_count': campaign.read_count,
            'last_run_at': campaign.last_run_at,
            'created_at': campaign.created_at,
            'updated_at': campaign.updated_at
        }
        return Response(campaign_data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching campaign {id}: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_404_NOT_FOUND
        )

# ==================================================
# UPDATE CAMPAIGN STATUS
# ==================================================
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_campaign_status(request, id):
    """
    Update campaign status - PUT /api/campaigns/{id}/status
    """
    try:
        serializer = UpdateCampaignSerializer(data=request.data)
        if serializer.is_valid():
            campaign = campaign_service.update(id, serializer.validated_data)
            return Response({
                'id': campaign.id,
                'status': campaign.status,
                'message': 'Campaign status updated successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error updating campaign status {id}: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# ==================================================
# UPDATE CAMPAIGN
# ==================================================
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_campaign(request, id):
    """
    Update campaign - PATCH /api/campaigns/{id}
    """
    try:
        serializer = UpdateCampaignSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            campaign = campaign_service.update(id, serializer.validated_data)
            return Response({
                'id': campaign.id,
                'campaign_name': campaign.campaign_name,
                'status': campaign.status,
                'message': 'Campaign updated successfully'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Error updating campaign {id}: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# ==================================================
# DELETE CAMPAIGN
# ==================================================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_campaign(request, id):
    """
    Delete campaign - DELETE /api/campaigns/{id}
    """
    try:
        result = campaign_service.remove(id)
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error deleting campaign {id}: {str(e)}")
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )