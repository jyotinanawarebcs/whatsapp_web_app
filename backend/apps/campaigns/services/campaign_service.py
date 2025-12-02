import logging
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import APIException, NotFound, PermissionDenied, ValidationError as DRFValidationError
from ..models import Campaign, CampaignContact, MessageTemplate
from ..utils.media_validator import validate_campaign_media_size, CampaignMediaValidationError, MEDIA_SIZE_LIMITS, ONE_MB
from virtualnumbers.services.numbers_service import numbers_service  # Add this import

logger = logging.getLogger(__name__)

class CampaignService:
    def __init__(self):
        self.logger = logger

    def create(self, dto_data, user):
        """
        Create new campaign - NestJS create() method ka equivalent
        """
        try:
            # Template check karega
            if dto_data.get('template_id'):
                self.ensure_template_availability(dto_data['template_id'])

            # Media validation
            media_data = {
                'media_type': dto_data.get('media_type'),
                'media_url': dto_data.get('media_url'),
                'media_name': dto_data.get('media_name'),
                'attachment_url': dto_data.get('attachment_url'),
                'mime_type': dto_data.get('media_mime_type'),
                'media_size': dto_data.get('media_size'),
            }
            
            try:
                validate_campaign_media_size(media_data)
            except CampaignMediaValidationError as error:
                limit_mb = (MEDIA_SIZE_LIMITS[error.media_type] / ONE_MB) if error.media_type in MEDIA_SIZE_LIMITS else 0
                raise DRFValidationError(
                    f"Uploaded {error.media_type} exceeds the maximum allowed size of {limit_mb:.2f} MB."
                )

            # Campaign create karega
            campaign_data = {
                # 'user': user,
                'campaign_name': dto_data.get('campaign_name'),
                'name': dto_data.get('name') or dto_data.get('campaign_name'),
                'template_id': dto_data.get('template_id'),
                'caption': dto_data.get('caption'),
                'media_url': dto_data.get('media_url'),
                'media_type': dto_data.get('media_type'),
                'media_name': dto_data.get('media_name'),
                'attachment_url': dto_data.get('attachment_url'),
                'cta_buttons': dto_data.get('cta_buttons', []),
                'status': dto_data.get('status', 'draft'),
                'scheduled_start': dto_data.get('scheduled_start'),
                'scheduled_end': dto_data.get('scheduled_end'),
            }
            
            campaign = Campaign.objects.create(**campaign_data)
            return campaign

        except DRFValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error creating campaign: {str(e)}")
            raise APIException("Failed to create campaign")

    def find_all(self, user_id):
        """
        Get all campaigns for user - NestJS findAll() method ka equivalent
        """
        try:
            campaigns = Campaign.objects.filter(user_id=user_id).order_by('-created_at')
            return campaigns
        except Exception as e:
            self.logger.error(f"Error fetching campaigns for user {user_id}: {str(e)}")
            raise APIException("Failed to fetch campaigns")

    def get_recent(self, user_id, limit=4):
        """
        Get recent campaigns - NestJS getRecent() method ka equivalent
        """
        try:
            campaigns = Campaign.objects.filter(user_id=user_id).order_by('-created_at')[:limit]
            return campaigns
        except Exception as e:
            self.logger.error(f"Error fetching recent campaigns for user {user_id}: {str(e)}")
            raise APIException("Failed to fetch recent campaigns")

    def get_dashboard_stats(self, user_id):
        """
        Get dashboard statistics - NestJS getDashboardStats() method ka equivalent
        """
        try:
            # Active campaigns count
            active_campaigns_count = Campaign.objects.filter(
                user_id=user_id, 
                status='active'
            ).count()
            
            # Sent today count (simplified)
            from django.utils import timezone
            from django.db.models import Sum
            today = timezone.now().date()
            sent_today_count = Campaign.objects.filter(
                user_id=user_id,
                last_run_at__date=today
            ).aggregate(total_sent=Sum('sent_count'))['total_sent'] or 0
            
            # Mock data for delivery rate (baad mein actual implementation)
            delivery_rate = '98.7%'
            
            return {
                'active_campaigns': active_campaigns_count,
                'active_campaigns_trend': {'value': '+2% from last week', 'is_positive': True},
                'sent_today': f"{sent_today_count:,}",
                'sent_today_trend': {'value': '+10% from yesterday', 'is_positive': True},
                'delivery_rate': delivery_rate,
                'delivery_rate_trend': {'value': '-0.2% from last week', 'is_positive': False},
            }
        except Exception as e:
            self.logger.error(f"Error getting dashboard stats for user {user_id}: {str(e)}")
            # Return default stats on error
            return {
                'active_campaigns': 0,
                'active_campaigns_trend': {'value': '0% change', 'is_positive': True},
                'sent_today': '0',
                'sent_today_trend': {'value': '0% change', 'is_positive': True},
                'delivery_rate': '0%',
                'delivery_rate_trend': {'value': '0% change', 'is_positive': True},
            }

    def find_one(self, id):
        """
        Get single campaign - NestJS findOne() method ka equivalent
        """
        try:
            campaign_id = int(id)
            campaign = Campaign.objects.get(id=campaign_id)
            return campaign
        except (ValueError, TypeError):
            raise NotFound(f"Invalid campaign ID: {id}")
        except Campaign.DoesNotExist:
            raise NotFound(f"Campaign with ID {id} not found")
        except Exception as e:
            self.logger.error(f"Error finding campaign with ID {id}: {str(e)}")
            raise APIException(f"Error retrieving campaign: {str(e)}")

    def update(self, id, dto_data):
        """
        Update campaign - NestJS update() method ka equivalent
        """
        try:
            campaign_id = int(id)
            existing_campaign = self.find_one(campaign_id)

            # Template check
            if dto_data.get('template_id'):
                self.ensure_template_availability(dto_data['template_id'])

            # Media validation
            media_data = {
                'media_type': dto_data.get('media_type', existing_campaign.media_type),
                'media_url': dto_data.get('media_url', existing_campaign.media_url),
                'media_name': dto_data.get('media_name', existing_campaign.media_name),
                'attachment_url': dto_data.get('attachment_url', existing_campaign.attachment_url),
                'mime_type': dto_data.get('media_mime_type'),
                'media_size': dto_data.get('media_size'),
            }
            
            validate_campaign_media_size(media_data)

            # Update campaign fields
            for field, value in dto_data.items():
                if hasattr(existing_campaign, field):
                    setattr(existing_campaign, field, value)
            
            existing_campaign.save()

            # Cleanup check
            if self.should_trigger_immediate_cleanup(dto_data.get('status')):
                self.schedule_immediate_cleanup(campaign_id)

            return existing_campaign

        except (DRFValidationError, NotFound):
            raise
        except Exception as e:
            self.logger.error(f"Error updating campaign with ID {id}: {str(e)}")
            raise APIException(f"Failed to update campaign: {str(e)}")

    def remove(self, id):
        """
        Delete campaign - NestJS remove() method ka equivalent
        """
        try:
            campaign_id = int(id)
            campaign = self.find_one(campaign_id)
            
            campaign.delete()
            self.schedule_immediate_cleanup(campaign_id)
            
            return {'message': 'Campaign deleted successfully'}

        except (NotFound, APIException):
            raise
        except Exception as e:
            self.logger.error(f"Error removing campaign with ID {id}: {str(e)}")
            raise APIException(f"Failed to delete campaign: {str(e)}")

    def run_campaign(self, dto_data, user):
        """
        Run campaign - NestJS runCampaign() method ka equivalent
        """
        try:
            campaign = self.get_campaign_for_user(dto_data['campaign_id'], user.id)

            if campaign.status in ['running', 'completed']:
                raise DRFValidationError('Campaign is already running or completed')

            # TODO: Virtual number integration baad mein
            assigned_number = {'id': 1, 'phone_number_id': 'test_number'}  # Mock for now

            should_start_now = dto_data.get('start_immediately', True)

            with transaction.atomic():
                managed_campaign = Campaign.objects.select_for_update().get(
                    id=campaign.id, 
                    user_id=user.id
                )

                # TODO: Contacts resolve karna baad mein
                selected_contacts = []  # Mock for now
                recipients_count = len(selected_contacts)

                if recipients_count <= 0:
                    raise DRFValidationError('No contacts available to run this campaign')

                # TODO: User credits check baad mein
                # if user.credits < recipients_count:
                #     raise PermissionDenied('Not enough credits')

                # Update campaign status
                managed_campaign.status = 'running' if should_start_now else 'scheduled'
                managed_campaign.recipients_count = recipients_count
                if should_start_now:
                    from django.utils import timezone
                    managed_campaign.last_run_at = timezone.now()
                
                managed_campaign.sent_count = 0
                managed_campaign.success_count = 0
                managed_campaign.failed_count = 0
                managed_campaign.read_count = 0
                managed_campaign.save()

                # TODO: Dispatch service integration baad mein
                dispatch_result = None
                if should_start_now:
                    dispatch_result = {
                        'batches': [],
                        'total_batches': 0
                    }

                return {
                    'campaign': managed_campaign,
                    'assigned_number': assigned_number,
                    'dispatch': dispatch_result
                }

        except (DRFValidationError, NotFound, PermissionDenied):
            raise
        except Exception as e:
            self.logger.error(f"Error running campaign: {str(e)}")
            raise APIException(f"Failed to run campaign: {str(e)}")

    def ensure_template_availability(self, template_id):
        """
        Check if template is available and approved
        """
        if not template_id:
            return

        try:
            template = MessageTemplate.objects.get(id=template_id)
            if template.approval_status != 'approved':
                raise DRFValidationError('Template must be approved before running campaigns')
        except MessageTemplate.DoesNotExist:
            raise NotFound(f"Template {template_id} does not exist")

    def get_campaign_for_user(self, campaign_id, user_id):
        """
        Get campaign for specific user
        """
        try:
            campaign = Campaign.objects.get(id=campaign_id, user_id=user_id)
            return campaign
        except Campaign.DoesNotExist:
            raise NotFound(f"Campaign {campaign_id} not found for this user")

    def should_trigger_immediate_cleanup(self, status):
        """
        Check if cleanup should be triggered
        """
        if not status:
            return False

        normalized = status.lower()
        return normalized in ['cancelled', 'canceled']

    def schedule_immediate_cleanup(self, campaign_id):
        """
        Schedule cleanup
        """
        try:
            # TODO: Cleanup service integration baad mein
            self.logger.info(f"Scheduled cleanup for campaign {campaign_id}")
        except Exception as e:
            self.logger.error(f"Failed to schedule immediate cleanup for campaign {campaign_id}: {str(e)}")


def resolve_virtual_number(self, preferred_id=None):
    """
    Virtual number assign karega - Now with actual numbers service integration
    
    Flow:
    1. If preferred_id provided: Use that specific number
    2. If no preferred_id: Let numbers service auto-select best number
    3. Validate number is active and available
    4. Return assigned virtual number
    
    Args:
        preferred_id: Specific virtual number ID to use
        
    Returns: VirtualNumber object
    """
    try:
        # Use the actual numbers service for number selection
        if preferred_id:
            # Get specific virtual number
            virtual_number = numbers_service.get_virtual_number_by_id(preferred_id)
            if not virtual_number:
                raise NotFound(f"Virtual number {preferred_id} not found")
            if virtual_number.status != 'active':
                raise DRFValidationError('Selected virtual number is not active')
            
            # Record usage for this number
            numbers_service.touch_usage(virtual_number.id)
            return virtual_number

        # Auto-select best available virtual number
        selected_number = numbers_service.select_random_active_number()
        
        if not selected_number:
            raise DRFValidationError('No active virtual number available to run campaign')

        return selected_number

    except Exception as e:
        self.logger.error(f"Error resolving virtual number: {str(e)}")
        raise APIException("Failed to assign virtual number")
# Service instance
campaign_service = CampaignService()