ONE_MB = 1024 * 1024
MEDIA_SIZE_LIMITS = {
    'image': 5 * ONE_MB,
    'video': 16 * ONE_MB,
    'document': 100 * ONE_MB,
    'audio': 16 * ONE_MB,
}

class CampaignMediaValidationError(Exception):
    def __init__(self, message, media_type=None):
        self.message = message
        self.media_type = media_type
        super().__init__(self.message)

def validate_campaign_media_size(media_data):
    """
    Validate media size based on WhatsApp limits
    """
    media_type = media_data.get('media_type')
    media_size = media_data.get('media_size')
    
    if not media_type or not media_size:
        return
    
    if media_type not in MEDIA_SIZE_LIMITS:
        raise CampaignMediaValidationError(
            f"Unsupported media type: {media_type}", 
            media_type
        )
    
    max_size = MEDIA_SIZE_LIMITS[media_type]
    
    if media_size > max_size:
        raise CampaignMediaValidationError(
            f"Media size exceeds limit for {media_type}",
            media_type
        )