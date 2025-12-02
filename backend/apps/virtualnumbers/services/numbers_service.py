import logging
import random
from django.db import models
from rest_framework.exceptions import APIException, NotFound, ValidationError as DRFValidationError
from ..models import BusinessNumber, VirtualNumber, VirtualNumberStatus, VirtualNumberQuality

logger = logging.getLogger(__name__)

# Default quality weights for number selection
DEFAULT_QUALITY_WEIGHTS = {
    VirtualNumberQuality.HIGH: 5,
    VirtualNumberQuality.MEDIUM: 3, 
    VirtualNumberQuality.LOW: 1,
    VirtualNumberQuality.UNKNOWN: 1,
}

class NumbersService:
    """
    Main service for managing virtual numbers and business numbers
    Handles number selection, switching, quality updates, and webhook processing
    """
    
    def __init__(self):
        self.logger = logger

    def get_business_number(self):
        """
        Get the primary business number configuration
        Returns: BusinessNumber object or None
        """
        try:
            return BusinessNumber.objects.first()
        except Exception as e:
            self.logger.error(f"Error getting business number: {str(e)}")
            raise APIException("Failed to get business number")

    def upsert_business_number(self, dto_data):
        """
        Create or update business number configuration
        Args:
            dto_data: Business number data from serializer
        Returns: Saved BusinessNumber object
        """
        try:
            existing = self.get_business_number()
            if existing:
                # Update existing business number
                for field, value in dto_data.items():
                    setattr(existing, field, value)
                existing.save()
                return existing
            else:
                # Create new business number
                business_number = BusinessNumber.objects.create(**dto_data)
                return business_number
        except Exception as e:
            self.logger.error(f"Error upserting business number: {str(e)}")
            raise APIException("Failed to update business number")

    def list_virtual_numbers(self):
        """
        Get all virtual numbers with intelligent sorting
        Sorting order: primary first, then by status, quality, and usage
        Returns: QuerySet of VirtualNumber objects
        """
        try:
            return VirtualNumber.objects.all().order_by(
                '-is_primary',  # Primary numbers first
                'status',       # Active status preferred
                'quality_rating', # Higher quality first
                'message_count_24h', # Lower usage first
                'id'            # Consistent ordering
            )
        except Exception as e:
            self.logger.error(f"Error listing virtual numbers: {str(e)}")
            raise APIException("Failed to list virtual numbers")

    def create_virtual_number(self, dto_data):
        """
        Create a new virtual number
        Args:
            dto_data: Virtual number data from serializer
        Returns: Created VirtualNumber object
        """
        try:
            # Get business number if provided
            business_number = None
            if dto_data.get('business_number_id'):
                business_number = self.get_business_number_by_id(dto_data['business_number_id'])
            
            # Create virtual number
            virtual_number = VirtualNumber.objects.create(
                business_number=business_number,
                waba_id=dto_data['waba_id'],
                phone_number_id=dto_data['phone_number_id'],
                access_token=dto_data['access_token'],
                status=dto_data.get('status', VirtualNumberStatus.ACTIVE),
                quality_rating=dto_data.get('quality_rating', VirtualNumberQuality.UNKNOWN),
                is_primary=dto_data.get('is_primary', True)
            )
            return virtual_number
            
        except Exception as e:
            self.logger.error(f"Error creating virtual number: {str(e)}")
            raise APIException("Failed to create virtual number")

    def update_virtual_number(self, number_id, dto_data):
        """
        Update an existing virtual number
        Args:
            number_id: ID of virtual number to update
            dto_data: Update data from serializer
        Returns: Updated VirtualNumber object
        """
        try:
            virtual_number = VirtualNumber.objects.get(id=number_id)
            
            # Update business number if provided
            if dto_data.get('business_number_id') is not None:
                business_number = self.get_business_number_by_id(dto_data['business_number_id'])
                virtual_number.business_number = business_number
            
            # Update other fields
            for field, value in dto_data.items():
                if field != 'business_number_id' and hasattr(virtual_number, field):
                    setattr(virtual_number, field, value)
            
            virtual_number.save()
            return virtual_number
            
        except VirtualNumber.DoesNotExist:
            raise NotFound("Virtual number not found")
        except Exception as e:
            self.logger.error(f"Error updating virtual number {number_id}: {str(e)}")
            raise APIException("Failed to update virtual number")

    def manual_switch(self, target_id=None, context=None):
        """
        Manually switch to a specific virtual number or auto-select one
        This is called by admin to force switch numbers
        
        Args:
            target_id: Specific number ID to switch to (optional)
            context: Switch context with reason and options
            
        Returns: Selected VirtualNumber object
        
        Flow:
        1. If target_id provided: Switch to that specific number
        2. If no target_id: Auto-select best available number
        3. Update number usage and primary status
        """
        try:
            if context is None:
                context = {'reason': 'manual switch'}
            
            # If specific target provided
            if target_id:
                target = VirtualNumber.objects.get(id=target_id)
                
                if target.status != VirtualNumberStatus.ACTIVE:
                    raise DRFValidationError('Selected virtual number is not active')
                
                # Mark as primary if not already
                if not target.is_primary:
                    target.is_primary = True
                    target.save()
                
                self.touch_usage(target.id)
                return target
            
            # Auto-select best number
            selected = self.select_random_active_number()
            
            if not selected:
                raise DRFValidationError('No eligible virtual numbers found for switching')
            
            return selected
            
        except VirtualNumber.DoesNotExist:
            raise NotFound(f"Target virtual number {target_id} not found")
        except Exception as e:
            self.logger.error(f"Error in manual switch: {str(e)}")
            raise APIException("Failed to switch virtual number")

    def record_message_usage(self, number_id, count_increment=1):
        """
        Record message usage for a virtual number
        Called by dispatch service when messages are sent
        
        Args:
            number_id: ID of virtual number
            count_increment: Number of messages to add to count
        """
        try:
            virtual_number = VirtualNumber.objects.get(id=number_id)
            virtual_number.message_count_24h += count_increment
            virtual_number.last_used_at = timezone.now()
            virtual_number.save()
        except Exception as e:
            self.logger.error(f"Error recording message usage for {number_id}: {str(e)}")

    def handle_quality_update(self, phone_number_id, status=None, quality=None):
        """
        Handle quality and status updates from webhooks
        Called by webhook controller when Meta sends updates
        
        Args:
            phone_number_id: WhatsApp phone number ID
            status: New status from webhook
            quality: New quality rating from webhook
            
        Returns: Updated VirtualNumber or None
        
        This method:
        - Updates number status and quality
        - Demotes primary status if number quality degrades
        - Logs the changes for monitoring
        """
        try:
            virtual_number = VirtualNumber.objects.get(phone_number_id=phone_number_id)
            
            previous_quality = virtual_number.quality_rating
            previous_status = virtual_number.status
            
            # Update status and quality if provided
            if status:
                virtual_number.status = status
            if quality:
                virtual_number.quality_rating = quality
            
            # Check if quality degraded
            quality_degraded = quality and self.is_quality_downgrade(previous_quality, quality)
            
            # Check if status became critical
            critical_statuses = [
                VirtualNumberStatus.BANNED, 
                VirtualNumberStatus.RESTRICTED, 
                VirtualNumberStatus.THROTTLED
            ]
            status_critical = status and status in critical_statuses
            
            # Demote from primary if quality degraded or status critical
            if (quality_degraded or status_critical) and virtual_number.is_primary:
                virtual_number.is_primary = False
            
            virtual_number.save()
            return virtual_number
            
        except VirtualNumber.DoesNotExist:
            return None
        except Exception as e:
            self.logger.error(f"Error handling quality update for {phone_number_id}: {str(e)}")
            return None

    def get_business_number_by_id(self, business_number_id):
        """
        Get business number by ID with validation
        """
        try:
            return BusinessNumber.objects.get(id=business_number_id)
        except BusinessNumber.DoesNotExist:
            raise NotFound("Business number not found")

    def select_random_active_number(self, options=None):
        """
        Smart virtual number selection with weighted random choice
        This is the core algorithm for auto number selection
        
        Args:
            options: Selection options (exclude_ids, max_message_count, etc.)
            
        Returns: Selected VirtualNumber or None
        
        Selection Logic:
        1. First try primary active numbers
        2. Then try any active numbers  
        3. Apply filters (exclusions, message limits, cooldown)
        4. Weighted random selection based on quality and usage
        """
        try:
            if options is None:
                options = {}
            
            # First get primary active numbers
            candidates = VirtualNumber.objects.filter(
                status=VirtualNumberStatus.ACTIVE,
                is_primary=True
            )
            
            # If no primary numbers, get any active numbers
            if not candidates:
                candidates = VirtualNumber.objects.filter(
                    status=VirtualNumberStatus.ACTIVE
                )
            
            if not candidates:
                return None
            
            # Apply filters
            filtered_candidates = self._filter_candidates(candidates, options)
            pool = filtered_candidates if filtered_candidates else candidates
            
            # Weighted random selection
            selected = self._weighted_random_selection(pool, options)
            if selected:
                self.touch_usage(selected.id)
            
            return selected
            
        except Exception as e:
            self.logger.error(f"Error in select_random_active_number: {str(e)}")
            return None

    def _filter_candidates(self, candidates, options):
        """
        Filter candidates based on selection options
        """
        from django.utils import timezone
        
        exclude_ids = options.get('exclude_ids', [])
        max_message_count_24h = options.get('max_message_count_24h')
        cooldown_minutes = options.get('cooldown_minutes')
        
        exclusion_set = set(exclude_ids)
        cooldown_ms = cooldown_minutes * 60_000 if cooldown_minutes else 0
        
        filtered = []
        for candidate in candidates:
            # Exclude specific IDs
            if candidate.id in exclusion_set:
                continue
            
            # Check message count limit
            if (max_message_count_24h is not None and 
                candidate.message_count_24h >= max_message_count_24h):
                continue
            
            # Check cooldown period
            if cooldown_ms and candidate.last_used_at:
                time_diff = (timezone.now() - candidate.last_used_at).total_seconds() * 1000
                if time_diff < cooldown_ms:
                    continue
            
            filtered.append(candidate)
        
        return filtered

    def _weighted_random_selection(self, pool, options):
        """
        Weighted random selection algorithm
        Weights are based on quality, usage, and cooldown
        """
        import random
        
        quality_weights = {**DEFAULT_QUALITY_WEIGHTS, **options.get('quality_weights', {})}
        max_message_count_24h = options.get('max_message_count_24h')
        cooldown_minutes = options.get('cooldown_minutes')
        
        weighted_pool = []
        
        for candidate in pool:
            # Quality weight
            quality_weight = quality_weights.get(candidate.quality_rating, 1)
            
            # Usage factor (prefer less used numbers)
            usage_factor = 1.0
            if max_message_count_24h:
                utilization = candidate.message_count_24h / max_message_count_24h
                usage_factor = max(0.25, 1.0 - min(utilization, 0.9))
            
            # Cooldown multiplier (prefer numbers not recently used)
            cooldown_multiplier = 1.0
            if cooldown_minutes:
                if not candidate.last_used_at:
                    cooldown_multiplier = 1.5  # Bonus for never used
                else:
                    from django.utils import timezone
                    time_diff = (timezone.now() - candidate.last_used_at).total_seconds() / 60
                    if time_diff >= cooldown_minutes:
                        cooldown_multiplier = 1.5  # Bonus for cooled down
                    else:
                        cooldown_multiplier = max(0.5, time_diff / cooldown_minutes)
            
            # Calculate final weight
            final_weight = quality_weight * usage_factor * cooldown_multiplier
            final_weight = max(final_weight, 0.1)  # Minimum weight
            
            weighted_pool.append({
                'candidate': candidate,
                'weight': final_weight
            })
        
        if not weighted_pool:
            return None
        
        # Random selection based on weights
        total_weight = sum(entry['weight'] for entry in weighted_pool)
        threshold = random.uniform(0, total_weight)
        
        current_weight = 0
        for entry in weighted_pool:
            current_weight += entry['weight']
            if current_weight >= threshold:
                return entry['candidate']
        
        # Fallback to last candidate
        return weighted_pool[-1]['candidate']

    def touch_usage(self, number_id):
        """
        Update last_used_at timestamp for a number
        """
        try:
            VirtualNumber.objects.filter(id=number_id).update(last_used_at=timezone.now())
        except Exception as e:
            self.logger.error(f"Error touching usage for {number_id}: {str(e)}")

    def is_quality_downgrade(self, previous_quality, new_quality):
        """
        Check if quality rating has been downgraded
        """
        quality_ranking = {
            VirtualNumberQuality.HIGH: 3,
            VirtualNumberQuality.MEDIUM: 2, 
            VirtualNumberQuality.LOW: 1,
            VirtualNumberQuality.UNKNOWN: 0,
        }
        
        previous_rank = quality_ranking.get(previous_quality, 0)
        new_rank = quality_ranking.get(new_quality, 0)
        
        return new_rank < previous_rank

# Service instance
numbers_service = NumbersService()