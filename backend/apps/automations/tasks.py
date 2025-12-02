from celery import shared_task
from django.utils import timezone
from django.conf import settings
import requests
import logging
from .models import Automation, AutomationLog
from contacts.models import Contact  # ✅ Correct import path

# Setup logging
logger = logging.getLogger(__name__)

@shared_task
def check_due_automations():
    """
    Check for automations that are due to run.
    This task is called periodically by Celery Beat.
    """
    try:
        now = timezone.now()
        
        # Find automations that are active and due to run
        due_automations = Automation.objects.filter(
            status='active',
            next_run__lte=now
        )
        
        # Schedule each due automation for execution
        for automation in due_automations:
            execute_automation_task.delay(automation.id)
            logger.info(f"Scheduled automation {automation.id} for execution")
        
        return f"Checked {due_automations.count()} due automations"
    
    except Exception as e:
        logger.error(f"Error checking due automations: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def execute_automation_task(automation_id):
    """
    Execute a specific automation - send WhatsApp messages to target contacts.
    """
    try:
        automation = Automation.objects.get(id=automation_id)
        
        # Only execute if automation is active
        if automation.status != 'active':
            return "Automation is not active"
        
        # ✅ CONTACTS APP SE CONTACTS IMPORT KARNA
        try:
            # Get all active contacts from contacts app
            contacts_queryset = Contact.objects.filter(is_active=True)
            
            # Convert to list format for processing
            contacts_list = []
            for contact in contacts_queryset:
                contacts_list.append({
                    "id": contact.id,
                    "name": contact.name or "Customer",
                    "phone": contact.phone,  # ✅ 'phone' field hai
                    "contact_obj": contact  # Keep reference for updates
                })
            
            logger.info(f"✅ Imported {len(contacts_list)} contacts from contacts app")
            
            # Agar koi contact nahi mila to warning
            if not contacts_list:
                logger.warning("No contacts found in contacts app")
                contacts_list = []  # Empty list - automation will show 0 contacts
        
        except Exception as import_error:
            logger.error(f"Error importing contacts: {str(import_error)}")
            # Fallback to test contacts if import fails
            contacts_list = [
                {"id": 1, "name": "Test User 1", "phone": "919022720168"},
                {"id": 2, "name": "Test User 2", "phone": "918879269714"},
            ]
            logger.info("Using fallback test contacts due to import error")
        
        total_contacts = len(contacts_list)
        successful_sends = 0
        errors = []
        
        # ✅ LOG AUTOMATION DETAILS
        logger.info(f"🔧 Automation: {automation.name} (ID: {automation.id})")
        logger.info(f"🔧 Message Template: {automation.message_template}")
        logger.info(f"🔧 Total Contacts to Process: {total_contacts}")
        
        for contact in contacts_list:
            try:
                # Format message with contact name
                # Check if template has {{name}} placeholder
                if "{{name}}" in automation.message_template:
                    message = automation.message_template.replace("{{name}}", contact["name"])
                else:
                    message = automation.message_template
                
                # ✅ LOG BEFORE SENDING
                logger.info(f"📤 Preparing to send to {contact['phone']} ({contact['name']})")
                
                # ✅ ACTUALLY SEND WHATSAPP MESSAGE
                success = send_whatsapp_message(contact["phone"], message, automation.cta_buttons)
                
                if success:
                    successful_sends += 1
                    
                    # ✅ UPDATE CONTACT'S LAST MESSAGE SENT IN CONTACTS APP
                    try:
                        contact_obj = contact["contact_obj"]
                        
                        # Check if fields exist before updating
                        if hasattr(contact_obj, 'last_message_sent'):
                            contact_obj.last_message_sent = timezone.now()
                        
                        if hasattr(contact_obj, 'message_count'):
                            current_count = getattr(contact_obj, 'message_count', 0)
                            contact_obj.message_count = current_count + 1
                        
                        # Mark as opted-in for WhatsApp (if field exists)
                        if hasattr(contact_obj, 'is_opted_in'):
                            contact_obj.is_opted_in = True
                        
                        contact_obj.save()
                        logger.debug(f"✅ Updated contact record for {contact['phone']}")
                    except Exception as update_error:
                        logger.warning(f"⚠️ Could not update contact record: {str(update_error)}")
                    
                    logger.info(f"✅ WhatsApp message sent to {contact['phone']}")
                else:
                    errors.append(f"Failed to send to {contact['phone']}")
                    logger.error(f"❌ Failed to send to {contact['phone']}")
                    
            except Exception as e:
                error_msg = f"Error for {contact['phone']}: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Update automation statistics
        automation.messages_sent += successful_sends
        automation.last_run = timezone.now()
        automation.next_run = calculate_next_run(automation)
        automation.save()
        
        # Determine execution status
        if total_contacts == 0:
            log_status = 'failed'
            errors.append("No contacts to send messages")
        elif successful_sends == total_contacts:
            log_status = 'success'
        elif successful_sends > 0:
            log_status = 'partial'
        else:
            log_status = 'failed'
        
        # Create log entry
        AutomationLog.objects.create(
            automation=automation,
            status=log_status,
            messages_sent=successful_sends,
            total_contacts=total_contacts,
            error_log='\n'.join(errors) if errors else None
        )
        
        result_msg = f"Automation {automation_id} executed: {successful_sends}/{total_contacts} messages sent"
        logger.info(result_msg)
        
        # ✅ SUMMARY LOG
        logger.info("="*60)
        logger.info("📊 EXECUTION SUMMARY")
        logger.info("="*60)
        logger.info(f"Automation: {automation.name}")
        logger.info(f"Contacts processed: {total_contacts}")
        logger.info(f"Messages sent successfully: {successful_sends}")
        logger.info(f"Errors: {len(errors)}")
        logger.info(f"Status: {log_status}")
        logger.info("="*60)
        
        return result_msg
    
    except Automation.DoesNotExist:
        logger.error(f"Automation {automation_id} not found")
        return "Automation not found"
    except Exception as e:
        logger.error(f"Error executing automation {automation_id}: {str(e)}")
        return f"Error: {str(e)}"

@shared_task
def schedule_single_automation(automation_id):
    """
    Schedule a single automation.
    """
    try:
        automation = Automation.objects.get(id=automation_id)
        logger.info(f"Automation {automation_id} marked for scheduling")
        return f"Automation {automation_id} will be checked periodically"
    
    except Exception as e:
        logger.error(f"Error scheduling automation {automation_id}: {str(e)}")
        return f"Error: {str(e)}"

def send_whatsapp_message(phone_number, message, cta_buttons=None):
    """
    Send message via WhatsApp Cloud API.
    """
    try:
        # ✅ CHECK WHATSAPP CREDENTIALS FIRST
        whatsapp_token = getattr(settings, 'WHATSAPP_TOKEN', '')
        whatsapp_phone_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
        
        if not whatsapp_token or whatsapp_token == 'your_whatsapp_token_here':
            logger.error("❌ WhatsApp token not set or is default value")
            return False
            
        if not whatsapp_phone_id or whatsapp_phone_id == 'your_phone_number_id_here':
            logger.error("❌ WhatsApp phone number ID not set or is default value")
            return False
        
        # Construct API URL
        url = f"https://graph.facebook.com/v17.0/{whatsapp_phone_id}/messages"
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {whatsapp_token}",
            "Content-Type": "application/json"
        }
        
        # Prepare payload based on whether we have CTA buttons
        if cta_buttons and len(cta_buttons) > 0:
            # Create interactive message with buttons
            buttons = []
            for index, btn in enumerate(cta_buttons[:3]):  # WhatsApp allows max 3 buttons
                if btn.get('type') == 'url':
                    buttons.append({
                        "type": "reply",
                        "reply": {
                            "id": f"btn_{index}",
                            "title": btn.get('title', 'Button')[:20]
                        }
                    })
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": message},
                    "action": {"buttons": buttons}
                }
            }
        else:
            # Simple text message
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": "text",
                "text": {"body": message}
            }
        
        logger.info(f"🔗 Calling WhatsApp API: {url}")
        logger.info(f"   Token first 10 chars: {whatsapp_token[:10]}...")
        
        # Make API request
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        # ✅ LOG DETAILED RESPONSE
        logger.info(f"   Status Code: {response.status_code}")
        
        # Check if request was successful
        if response.status_code == 200:
            logger.info(f"✅ WhatsApp API Success for {phone_number}")
            
            # Log message ID if available
            try:
                response_json = response.json()
                if 'messages' in response_json:
                    message_id = response_json['messages'][0]['id']
                    logger.info(f"   Message ID: {message_id}")
            except:
                pass
                
            return True
        else:
            error_text = response.text[:500]
            logger.error(f"❌ WhatsApp API error {response.status_code}: {error_text}")
            
            # Parse error for better debugging
            try:
                import json
                error_data = json.loads(error_text)
                if 'error' in error_data:
                    error_details = error_data['error']
                    logger.error(f"   Error Type: {error_details.get('type', 'Unknown')}")
                    logger.error(f"   Error Code: {error_details.get('code', 'Unknown')}")
                    logger.error(f"   Error Message: {error_details.get('message', 'Unknown')}")
                    
                    # Handle specific errors
                    error_message = error_details.get('message', '')
                    if 'not have an account' in error_message:
                        logger.error("   ❗ This phone number does not have WhatsApp")
                    elif 'template' in error_message:
                        logger.error("   ❗ Template issue - check if template is approved")
                    elif 'rate limit' in error_message:
                        logger.error("   ⚠️ Rate limit exceeded - waiting before next attempt")
            except:
                pass
            
            return False
    
    except requests.exceptions.Timeout:
        logger.error("❌ WhatsApp API timeout")
        return False
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp message: {str(e)}")
        return False

def calculate_next_run(automation):
    """
    Calculate next run time based on automation schedule.
    """
    from datetime import timedelta
    
    if automation.cron_expression:
        # Use cron expression to calculate next run
        try:
            from croniter import croniter
            from datetime import datetime
            iter = croniter(automation.cron_expression, timezone.now())
            return iter.get_next(datetime)
        except Exception as e:
            logger.error(f"Error calculating next run from cron: {str(e)}")
    
    # Fallback based on schedule type
    if automation.schedule_type == 'daily':
        return timezone.now() + timedelta(days=1)
    elif automation.schedule_type == 'weekly':
        return timezone.now() + timedelta(weeks=1)
    elif automation.schedule_type == 'monthly':
        return timezone.now() + timedelta(days=30)
    else:
        # Default to daily
        return timezone.now() + timedelta(days=1)