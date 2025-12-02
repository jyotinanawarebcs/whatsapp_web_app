from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services.numbers_service import numbers_service
from .models import VirtualNumberStatus, VirtualNumberQuality
import logging
import json

logger = logging.getLogger(__name__)

# ==================================================
# META WEBHOOK HANDLER
# ==================================================
@api_view(['POST'])
async def handle_meta_webhook(request):
    """
    Handle incoming webhooks from Meta (Facebook) for number status updates
    Endpoint: POST /api/webhooks/meta
    
    This webhook receives:
    - Quality updates for phone numbers
    - Status changes (restricted, banned, throttled)
    - Usage limits and health metrics
    
    Flow:
    1. Parse webhook payload from Meta
    2. Extract phone number ID and changes
    3. Process status and quality updates
    4. Update virtual number in database
    5. Log the webhook for monitoring
    """
    try:
        payload = request.data
        
        # Log incoming webhook for debugging
        logger.info(f"Received Meta webhook: {json.dumps(payload, default=str)}")
        
        if not payload.get('entry'):
            logger.warning('Received Meta webhook with no entries')
            return Response({'received': True}, status=status.HTTP_200_OK)

        # Process each entry in the webhook
        for entry in payload['entry']:
            for change in entry.get('changes', []):
                await process_change(change.get('field'), change.get('value'))

        return Response({'received': True}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error processing Meta webhook: {str(e)}")
        return Response({'received': True}, status=status.HTTP_200_OK)  # Always return 200 to Meta

def process_change(field, value):
    """
    Process individual change from Meta webhook
    
    Args:
        field: The type of change (quality_update, etc.)
        value: The change data containing phone number info
    """
    if not value:
        return

    # Extract phone number ID from different possible fields
    phone_number_id = (
        value.get('metadata', {}).get('phone_number_id') or
        value.get('phone_number_id') or
        value.get('id') or 
        value.get('recipient_id')
    )

    if not phone_number_id:
        logger.debug('Skipping webhook change without phone_number_id')
        return

    # Initialize status and quality variables
    status = None
    quality = None

    # Process quality updates
    if field == 'quality_update' or value.get('quality_rating'):
        quality = map_quality(value.get('quality_rating') or value.get('current_limit', {}).get('quality_rating'))

    # Process status updates from different field names
    if value.get('event') == 'RESTRICTED' or value.get('messaging_product_status'):
        status = map_status(value.get('event') or value.get('messaging_product_status'))

    if value.get('number_status'):
        status = map_status(value.get('number_status'))

    # Process statuses array (multiple status updates)
    if value.get('statuses') and isinstance(value['statuses'], list):
        latest = value['statuses'][0]
        if latest.get('status'):
            status = map_status(latest['status'])
        if latest.get('quality'):
            quality = map_quality(latest['quality'])

    # If no actionable updates, log and return
    if not status and not quality:
        logger.debug(f"No actionable status/quality change detected for {phone_number_id}")
        return

    # Update the virtual number in database
    updated_number = numbers_service.handle_quality_update(phone_number_id, status, quality)

    # Log the webhook processing (you can save to database here)
    logger.info(f"Processed webhook for {phone_number_id}: status={status}, quality={quality}")

def map_status(input_status):
    """
    Map Meta webhook status to our internal status enum
    
    Args:
        input_status: Status string from Meta webhook
        
    Returns: VirtualNumberStatus enum value or None
    """
    if not input_status:
        return None

    normalized = input_status.lower()

    # Map Meta status values to our internal status
    status_mapping = {
        'restricted': VirtualNumberStatus.RESTRICTED,
        'temporarily restricted': VirtualNumberStatus.RESTRICTED,
        'throttled': VirtualNumberStatus.THROTTLED,
        'rate_limited': VirtualNumberStatus.THROTTLED,
        'banned': VirtualNumberStatus.BANNED,
        'blocked': VirtualNumberStatus.BANNED,
        'disconnected': VirtualNumberStatus.DISCONNECTED,
        'active': VirtualNumberStatus.ACTIVE,
        'live': VirtualNumberStatus.ACTIVE,
        'ok': VirtualNumberStatus.ACTIVE,
    }

    return status_mapping.get(normalized)

def map_quality(input_quality):
    """
    Map Meta webhook quality to our internal quality enum
    
    Args:
        input_quality: Quality string from Meta webhook
        
    Returns: VirtualNumberQuality enum value or None
    """
    if not input_quality:
        return None

    normalized = input_quality.lower()

    # Map Meta quality values to our internal quality ratings
    quality_mapping = {
        'green': VirtualNumberQuality.HIGH,
        'high': VirtualNumberQuality.HIGH,
        'yellow': VirtualNumberQuality.MEDIUM,
        'medium': VirtualNumberQuality.MEDIUM,
        'red': VirtualNumberQuality.LOW,
        'low': VirtualNumberQuality.LOW,
    }

    return quality_mapping.get(normalized, VirtualNumberQuality.UNKNOWN)