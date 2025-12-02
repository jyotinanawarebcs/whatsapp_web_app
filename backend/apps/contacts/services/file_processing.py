import csv
import pandas as pd
from ..models import Contact
from django.db import transaction
import logging
import re
from django.db.models import Q
import re
from datetime import datetime

logger = logging.getLogger(__name__)
BATCH_SIZE = 1000

def parse_date_robust(value):
    """
    More robust date parsing that handles various edge cases
    """
    if not value or value in ['', 'nan', 'None', 'null', 'NaT']:
        return None
    
    original_value = str(value).strip()
    print(f"🔍 DEBUG: Original date value: '{original_value}'")
    
    # Remove all non-alphanumeric characters except / and -
    cleaned = re.sub(r'[^a-zA-Z0-9/-]', '', original_value)
    cleaned = cleaned.strip()
    
    print(f"🔍 DEBUG: After cleaning: '{cleaned}'")
    
    if not cleaned:
        return None
    
    # Try different date formats
    formats_to_try = [
        '%d/%b/%Y',  # 01/JAN/1988
        '%d-%b-%Y',  # 01-JAN-1988
        '%d/%m/%Y',  # 01/01/1988
        '%d-%m-%Y',  # 01-01-1988
        '%m/%d/%Y',  # 01/15/1988 (American)
        '%Y-%m-%d',  # 1988-01-01
        '%Y/%m/%d',  # 1988/01/01
    ]
    
    for fmt in formats_to_try:
        try:
            # Convert to uppercase for month abbreviations
            date_obj = datetime.strptime(cleaned.upper(), fmt)
            result = date_obj.strftime('%Y-%m-%d')
            print(f"🔍 DEBUG: Successfully parsed '{original_value}' -> '{result}' using format '{fmt}'")
            return result
        except ValueError:
            continue
    
    print(f"🔍 DEBUG: Could not parse date in any format: '{original_value}'")
    return None

def process_uploaded_file(file_path, filename, file_ext):
    """
    Main function to process uploaded files
    """
    print(f"🔍 DEBUG: Processing file: {filename}")
    
    try:
        if file_ext in ['csv', 'txt']:
            result = process_csv_file(file_path, filename)
        elif file_ext in ['xls', 'xlsx']:
            result = process_excel_file(file_path, filename)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")
        
        print(f"🔍 DEBUG: Final result: {result}")
        return result
        
    except Exception as e:
        print(f"🔍 DEBUG: Error in process_uploaded_file: {str(e)}")
        raise

def process_excel_file(file_path, filename):
    """
    Enhanced Excel processing based on NestJS logic
    """
    contact_map = {}  # Use dict instead of Map
    
    try:
        print(f"🔍 DEBUG: Processing Excel file: {filename}")
        
        # Read all sheets
        df_dict = pd.read_excel(file_path, sheet_name=None)
        print(f"🔍 DEBUG: Workbook sheets: {list(df_dict.keys())}")
        
        for sheet_name, sheet in df_dict.items():
            print(f"🔍 DEBUG: Processing sheet: {sheet_name}")
            
            # Convert to object format first (with headers)
            sheet = sheet.astype(str)
            sheet = sheet.replace('nan', '')
            sheet = sheet.replace('None', '')
            
            json_data = sheet.to_dict('records')
            print(f"🔍 DEBUG: Sheet data (object format): {len(json_data)} rows")
            
            if json_data:
                print('🔍 DEBUG: Processing data in object format')
                for row in json_data:
                    contact_data = extract_all_fields_from_object_row(row)
                    if contact_data.get('phone'):
                        contact_map[contact_data['phone']] = contact_data
            
            # If no data in object format, try array format
            if not contact_map:
                array_data = sheet.values.tolist()
                headers = sheet.columns.tolist()
                print(f"🔍 DEBUG: Sheet data (array format): {len(array_data)} rows")
                
                if len(array_data) > 1:
                    print('🔍 DEBUG: Processing data in array format')
                    for i, row in enumerate(array_data):
                        if i == 0:  # Skip header row
                            continue
                        contact_data = extract_all_fields_from_array_row(row, headers)
                        if contact_data.get('phone'):
                            contact_map[contact_data['phone']] = contact_data
        
        contacts_found = list(contact_map.values())
        print(f"🔍 DEBUG: Total unique contacts found: {len(contacts_found)}")
        
        # Process contacts in batches
        result = save_contacts_batch_enhanced(contacts_found, filename)
        return result
        
    except Exception as e:
        print(f"🔍 DEBUG: Error processing Excel file: {str(e)}")
        return {
            'error': f'Excel processing error: {str(e)}',
            'total_processed': 0,
            'inserted': 0,
            'updated': 0
        }

def process_csv_file(file_path, filename):
    """
    Enhanced CSV processing based on NestJS logic
    """
    contact_map = {}
    
    try:
        print(f"🔍 DEBUG: Processing CSV file: {filename}")
        
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # Try different encodings if utf-8 fails
            reader = csv.DictReader(csvfile)
            
            for row_num, row in enumerate(reader):
                contact_data = extract_all_fields_from_object_row(row)
                if contact_data.get('phone'):
                    contact_map[contact_data['phone']] = contact_data
                
                # Debug first few rows
                if row_num < 3:
                    print(f"🔍 DEBUG: Row {row_num}: {contact_data}")
        
        contacts_found = list(contact_map.values())
        print(f"🔍 DEBUG: Total unique contacts found: {len(contacts_found)}")
        
        result = save_contacts_batch_enhanced(contacts_found, filename)
        return result
        
    except Exception as e:
        print(f"🔍 DEBUG: Error processing CSV file: {str(e)}")
        return {
            'error': f'CSV processing error: {str(e)}',
            'total_processed': 0,
            'inserted': 0,
            'updated': 0
        }

def extract_all_fields_from_object_row(row):
    """
    Enhanced field extraction with robust date parsing
    """
    if not row or not isinstance(row, dict):
        return {}
    
    return {
        'phone': extract_phone(row),
        'name': extract_name(row),
        'aadhar': extract_field(row, ['aadhar', 'aadhar number', 'aadhar_no', 'aadharnumber', 'aadhar card']),
        'father_name': extract_field(row, ['father', 'father name', 'father_name', 'fathername', 'fathers name']),
        'gender': extract_field(row, ['gender', 'sex']),
        'email_id': extract_field(row, ['email', 'email_id', 'emailid', 'email address', 'emailaddress']),
        'city': extract_field(row, ['city']),
        'state': extract_field(row, ['state']),
        'nationality': extract_field(row, ['nationality', 'country']),
        'dob': parse_date_robust(extract_field(row, ['dob', 'date of birth', 'birthdate', 'birth date'])),  # Use robust parser
        'other_mobile': extract_field(row, ['other mobile', 'other_mobile', 'alternate mobile', 'alternatemobile', 'other phone']),
        'permanent': extract_field(row, ['permanent', 'permanent address', 'address', 'permanent_address']),
        'pincode': extract_field(row, ['pincode', 'pin code', 'zipcode', 'postal code']),
    }

def extract_all_fields_from_array_row(row, headers=None):
    """
    Extract from array row using headers
    """
    if not isinstance(row, list) or not headers:
        return {}
    
    # Convert array to object using headers
    row_object = {}
    for i, header in enumerate(headers):
        if i < len(row):
            row_object[header] = row[i]
    
    return extract_all_fields_from_object_row(row_object)

def extract_phone(row):
    """
    Enhanced phone extraction based on NestJS logic
    """
    phone = extract_field(row, [
        'phone', 'mobile', 'cell', 'telephone', 'contact', 'number',
        'phone number', 'mobile number', 'contact number'
    ])
    return normalize_phone_enhanced(phone)

def extract_name(row):
    """
    Enhanced name extraction
    """
    name = extract_field(row, [
        'name', 'fullname', 'full name', 'firstname', 'first name',
        'lastname', 'last name', 'contact name', 'person name'
    ])
    return normalize_name(name)

def extract_field(row, possible_keys):
    """
    Enhanced field extraction with multiple matching strategies
    """
    if not row or not isinstance(row, dict):
        return None
    
    # Try exact match first
    for key in possible_keys:
        if key in row and row[key] not in [None, '', 'nan', 'None']:
            value = str(row[key]).strip()
            if value:
                return value
    
    # Try case-insensitive match
    lower_case_keys = [k.lower() for k in possible_keys]
    for actual_key, value in row.items():
        if actual_key.lower() in lower_case_keys and value not in [None, '', 'nan', 'None']:
            value_str = str(value).strip()
            if value_str:
                return value_str
    
    # Try partial match
    for actual_key, value in row.items():
        if value in [None, '', 'nan', 'None']:
            continue
            
        lower_actual_key = actual_key.lower()
        for possible_key in possible_keys:
            if possible_key.lower() in lower_actual_key:
                value_str = str(value).strip()
                if value_str:
                    return value_str
    
    return None

# def normalize_phone_enhanced(value):
#     """
#     Enhanced phone normalization that handles Excel float conversion
#     """
#     if value in [None, '', 'nan', 'None']:
#         return None
    
#     raw = str(value).strip()
#     if not raw:
#         return None
    
#     print(f"🔍 DEBUG: Raw phone: '{raw}'")
    
#     # Handle Excel float conversion (numbers ending with .0)
#     if raw.endswith('.0'):
#         raw = raw[:-2]  # Remove the '.0'
#         print(f"🔍 DEBUG: Removed .0 suffix: '{raw}'")
    
#     # Remove all non-digit characters except +
#     cleaned = re.sub(r'[^\d+]', '', raw)
#     if not cleaned:
#         return None
    
#     print(f"🔍 DEBUG: Cleaned phone: '{cleaned}'")
    
#     # Validate phone number format (6-15 digits, optional +)
#     # For Indian numbers: typically 10 digits, sometimes with country code
#     if not re.match(r'^\+?\d{6,15}$', cleaned):
#         print(f"🔍 DEBUG: Invalid phone format: '{cleaned}'")
#         return None
    
#     # Handle specific cases:
    
#     # Convert 00 prefix to +
#     if cleaned.startswith('00'):
#         normalized = '+' + cleaned[2:]
#         print(f"🔍 DEBUG: Converted 00 prefix: '{normalized}'")
#         return normalized
    
#     # Ensure + prefix for international numbers
#     if cleaned.startswith('+'):
#         print(f"🔍 DEBUG: Valid international phone: '{cleaned}'")
#         return cleaned
    
#     # For Indian numbers: should be 10 digits
#     if len(cleaned) == 10:
#         print(f"🔍 DEBUG: Valid Indian phone: '{cleaned}'")
#         return cleaned
#     elif len(cleaned) == 11 and cleaned.startswith('0'):
#         # Remove leading 0 (like 07887663142 -> 7887663142)
#         normalized = cleaned[1:]
#         print(f"🔍 DEBUG: Removed leading 0: '{normalized}'")
#         return normalized
#     elif len(cleaned) == 12 and cleaned.startswith('91'):
#         # Remove country code (like 917887663142 -> 7887663142)
#         normalized = cleaned[2:]
#         print(f"🔍 DEBUG: Removed country code 91: '{normalized}'")
#         return normalized
#     else:
#         print(f"🔍 DEBUG: Invalid phone length: {len(cleaned)} digits")
#         return None

def normalize_phone_enhanced(value):
    """
    Enhanced phone normalization that handles Excel float conversion
    """
    if value in [None, '', 'nan', 'None']:
        return None
    
    raw = str(value).strip()
    if not raw:
        return None
    
    print(f"🔍 DEBUG: Raw phone: '{raw}'")
    
    # Handle Excel float conversion (numbers ending with .0)
    if raw.endswith('.0'):
        raw = raw[:-2]  # Remove the '.0'
        print(f"🔍 DEBUG: Removed .0 suffix: '{raw}'")
    
    # Remove all non-digit characters except +
    cleaned = re.sub(r'[^\d+]', '', raw)
    if not cleaned:
        return None
    
    print(f"🔍 DEBUG: Cleaned phone: '{cleaned}'")
    
    # Validate phone number format (6-15 digits, optional +)
    # For Indian numbers: typically 10 digits, sometimes with country code
    if not re.match(r'^\+?\d{6,15}$', cleaned):
        print(f"🔍 DEBUG: Invalid phone format: '{cleaned}'")
        return None
    
    # Handle specific cases:
    
    # Convert 00 prefix to +
    if cleaned.startswith('00'):
        normalized = '+' + cleaned[2:]
        print(f"🔍 DEBUG: Converted 00 prefix: '{normalized}'")
        return normalized
    
    # Ensure + prefix for international numbers
    if cleaned.startswith('+'):
        print(f"🔍 DEBUG: Valid international phone: '{cleaned}'")
        return cleaned
    
    # For Indian numbers: should be 10 digits
    if len(cleaned) == 10:
        print(f"🔍 DEBUG: Valid Indian phone: '{cleaned}'")
        return cleaned
    elif len(cleaned) == 11 and cleaned.startswith('0'):
        # Remove leading 0 (like 07887663142 -> 7887663142)
        normalized = cleaned[1:]
        print(f"🔍 DEBUG: Removed leading 0: '{normalized}'")
        return normalized
    elif len(cleaned) == 12 and cleaned.startswith('91'):
        # Remove country code (like 917887663142 -> 7887663142)
        normalized = cleaned[2:]
        print(f"🔍 DEBUG: Removed country code 91: '{normalized}'")
        return normalized
    elif len(cleaned) > 12:
        # 🔥 NEW: Handle very long numbers - take only last 10 digits
        normalized = cleaned[-10:]
        print(f"🔍 DEBUG: Truncated long phone to 10 digits: '{normalized}'")
        return normalized
    else:
        print(f"🔍 DEBUG: Invalid phone length: {len(cleaned)} digits")
        return None

def normalize_name(value):
    """
    Enhanced name normalization
    """
    if value in [None, '', 'nan', 'None']:
        return None
    
    name = str(value).strip()
    if not name or name.lower() in ['null', 'undefined', 'nan']:
        return None
    
    # Remove extra whitespace
    normalized = re.sub(r'\s+', ' ', name).strip()
    if normalized and len(normalized) <= 255:
        return normalized
    
    return None

# def save_contacts_batch_enhanced(contacts_list, filename):
#     """
#     Enhanced batch saving based on NestJS logic
#     """
#     if not contacts_list:
#         return {
#             'total_processed': 0,
#             'inserted': 0,
#             'updated': 0,
#             'message': 'No contacts to process'
#         }
    
#     total = len(contacts_list)
#     inserted_count = 0
#     updated_count = 0
    
#     print(f"🔍 DEBUG: Starting to process {total} contacts")
    
#     try:
#         with transaction.atomic():
#             # Get existing contacts by phone
#             existing_phones = set(Contact.objects.filter(
#                 phone__in=[c['phone'] for c in contacts_list]
#             ).values_list('phone', flat=True))
            
#             print(f"🔍 DEBUG: Found {len(existing_phones)} existing contacts")
            
#             contacts_to_create = []
#             contacts_to_update = []
            
#             # Separate create and update operations
#             for contact_data in contacts_list:
#                 phone = contact_data['phone']
                
#                 if phone in existing_phones:
#                     contacts_to_update.append(contact_data)
#                 else:
#                     contact_data['source_file'] = filename
#                     contacts_to_create.append(Contact(**contact_data))
            
#             # Bulk create new contacts
#             if contacts_to_create:
#                 print(f"🔍 DEBUG: Creating {len(contacts_to_create)} new contacts")
#                 for i in range(0, len(contacts_to_create), BATCH_SIZE):
#                     batch = contacts_to_create[i:i + BATCH_SIZE]
#                     Contact.objects.bulk_create(batch)
#                     inserted_count += len(batch)
#                     print(f"🔍 DEBUG: Created batch {i//BATCH_SIZE + 1}")
            
#             # Update existing contacts
#             if contacts_to_update:
#                 print(f"🔍 DEBUG: Updating {len(contacts_to_update)} existing contacts")
#                 for contact_data in contacts_to_update:
#                     # Get the existing contact
#                     existing = Contact.objects.filter(phone=contact_data['phone']).first()
#                     if existing:
#                         # Update fields
#                         for field, value in contact_data.items():
#                             if value and field != 'phone':  # Don't update phone
#                                 setattr(existing, field, value)
#                         existing.source_file = filename
#                         existing.save()
#                         updated_count += 1
            
#             print(f"🔍 DEBUG: Completed: {inserted_count} inserted, {updated_count} updated")
            
#             return {
#                 'total_processed': total,
#                 'inserted': inserted_count,
#                 'updated': updated_count,
#                 'message': f'Successfully processed {total} contacts'
#             }
    
#     except Exception as e:
#         print(f"🔍 DEBUG: Error in batch processing: {str(e)}")
#         return {
#             'error': f'Database error: {str(e)}',
#             'total_processed': total,
#             'inserted': 0,
#             'updated': 0
#         }
    

def save_contacts_batch_enhanced(contacts_list, filename):
    """
    Enhanced batch saving with better error handling
    """
    if not contacts_list:
        return {
            'total_processed': 0,
            'inserted': 0,
            'updated': 0,
            'message': 'No contacts to process'
        }
    
    total = len(contacts_list)
    inserted_count = 0
    updated_count = 0
    error_count = 0
    error_details = []
    
    print(f"🔍 DEBUG: Starting to process {total} contacts")
    
    try:
        with transaction.atomic():
            # Get existing contacts by phone
            existing_phones = set(Contact.objects.filter(
                phone__in=[c['phone'] for c in contacts_list if c.get('phone')]
            ).values_list('phone', flat=True))
            
            print(f"🔍 DEBUG: Found {len(existing_phones)} existing contacts")
            
            contacts_to_create = []
            contacts_to_update = []
            
            # Separate create and update operations with validation
            for i, contact_data in enumerate(contacts_list):
                phone = contact_data.get('phone')
                
                if not phone:
                    error_count += 1
                    error_details.append(f"Row {i}: Missing phone number")
                    continue
                
                # Validate phone length before saving
                if len(phone) > 10:
                    # Auto-truncate long numbers
                    contact_data['phone'] = phone[-10:]
                    print(f"🔍 DEBUG: Truncated phone {phone} to {contact_data['phone']}")
                
                if phone in existing_phones:
                    contacts_to_update.append(contact_data)
                else:
                    contact_data['source_file'] = filename
                    contacts_to_create.append(Contact(**contact_data))
            
            # Bulk create new contacts
            if contacts_to_create:
                print(f"🔍 DEBUG: Creating {len(contacts_to_create)} new contacts")
                try:
                    for i in range(0, len(contacts_to_create), BATCH_SIZE):
                        batch = contacts_to_create[i:i + BATCH_SIZE]
                        Contact.objects.bulk_create(batch)
                        inserted_count += len(batch)
                        print(f"🔍 DEBUG: Created batch {i//BATCH_SIZE + 1}")
                except Exception as e:
                    print(f"🔍 DEBUG: Error in bulk create: {str(e)}")
                    error_count += len(contacts_to_create)
                    error_details.append(f"Bulk create error: {str(e)}")
            
            # Update existing contacts
            if contacts_to_update:
                print(f"🔍 DEBUG: Updating {len(contacts_to_update)} existing contacts")
                for contact_data in contacts_to_update:
                    try:
                        # Get the existing contact
                        existing = Contact.objects.filter(phone=contact_data['phone']).first()
                        if existing:
                            # Update fields
                            for field, value in contact_data.items():
                                if value and field != 'phone':  # Don't update phone
                                    setattr(existing, field, value)
                            existing.source_file = filename
                            existing.save()
                            updated_count += 1
                    except Exception as e:
                        error_count += 1
                        error_details.append(f"Update error for {contact_data['phone']}: {str(e)}")
                        print(f"🔍 DEBUG: Error updating {contact_data['phone']}: {str(e)}")
            
            print(f"🔍 DEBUG: Completed: {inserted_count} inserted, {updated_count} updated, {error_count} errors")
            
            result = {
                'total_processed': total,
                'inserted': inserted_count,
                'updated': updated_count,
                'errors': error_count,
                'message': f'Successfully processed {total} contacts'
            }
            
            if error_count > 0:
                result['error_details'] = error_details[:10]  # First 10 errors only
                result['message'] = f'Processed with {error_count} errors'
            
            return result
    
    except Exception as e:
        print(f"🔍 DEBUG: Error in batch processing: {str(e)}")
        return {
            'error': f'Database error: {str(e)}',
            'total_processed': total,
            'inserted': 0,
            'updated': 0,
            'errors': total
        }

    