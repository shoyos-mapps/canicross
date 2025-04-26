from celery import shared_task
import logging
import re
from datetime import datetime
from registrations.models import Document

logger = logging.getLogger(__name__)

@shared_task
def process_document_with_ocr(document_id):
    """
    Process the document with OCR to extract text.
    This is a placeholder task that would integrate with an actual OCR service.
    """
    try:
        document = Document.objects.get(id=document_id)
        
        # This is where you would call an external OCR service like Google Vision, AWS Textract, etc.
        # For development, we're just setting a placeholder status
        
        # Simulated OCR extraction
        document.ocr_status = 'completed'
        document.ocr_raw_text = f"This is a simulated OCR extraction for document {document.id}."
        document.save()
        
        # Trigger vaccine analysis task
        analyze_vaccine_document.delay(document_id)
        
        return f"Document {document_id} processed with OCR successfully"
    except Document.DoesNotExist:
        logger.error(f"Document with ID {document_id} not found")
        return f"Error: Document with ID {document_id} not found"
    except Exception as e:
        logger.error(f"Error processing document with OCR: {str(e)}")
        return f"Error processing document: {str(e)}"

@shared_task
def analyze_vaccine_document(document_id):
    """
    Analyze the OCR-extracted text to find vaccines and their dates.
    This is a placeholder task that would implement more sophisticated NLP.
    """
    try:
        document = Document.objects.get(id=document_id)
        registration = document.registration
        event = registration.race.event
        
        # Skip if not a vaccination document
        if document.document_type != 'vaccination_record':
            return f"Document {document_id} is not a vaccination record, skipping analysis"
        
        # Get required vaccines from event configuration
        required_vaccines = event.required_vaccines
        
        # This is where you would implement more sophisticated text analysis
        # For now, just a simple regex pattern matching demonstration
        ocr_text = document.ocr_raw_text
        
        # Simulated analysis
        found_vaccines = []
        issues = []
        
        # Simple regex pattern for date detection (DD/MM/YYYY)
        date_pattern = r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})'
        
        # Check for each required vaccine (very simplistic check for demonstration)
        for vaccine in required_vaccines:
            # See if the vaccine name appears in the text
            if re.search(rf'\b{re.escape(vaccine)}\b', ocr_text, re.IGNORECASE):
                # Look for a date near the vaccine name
                vaccine_mention = re.search(rf'\b{re.escape(vaccine)}.{{0,50}}', ocr_text, re.IGNORECASE)
                if vaccine_mention:
                    date_match = re.search(date_pattern, vaccine_mention.group(0))
                    if date_match:
                        day, month, year = map(int, date_match.groups())
                        vaccine_date = datetime(year, month, day).date()
                        event_date = event.start_date
                        
                        if vaccine_date > event_date:
                            found_vaccines.append({'name': vaccine, 'valid': True})
                        else:
                            found_vaccines.append({'name': vaccine, 'valid': False})
                            issues.append(f"Vaccine {vaccine} appears to have expired")
                    else:
                        issues.append(f"Could not find date for vaccine {vaccine}")
            else:
                issues.append(f"Could not find vaccine {vaccine}")
        
        # Save analysis results
        document.ocr_analysis_result = {
            'found_vaccines': found_vaccines,
            'issues': issues
        }
        document.save()
        
        # Update registration status based on analysis
        if not issues:
            registration.ai_vaccine_status = 'ok'
        elif len(found_vaccines) > 0:
            registration.ai_vaccine_status = 'issue'
        else:
            registration.ai_vaccine_status = 'error'
        
        registration.save()
        
        return f"Document {document_id} analyzed successfully"
    except Document.DoesNotExist:
        logger.error(f"Document with ID {document_id} not found")
        return f"Error: Document with ID {document_id} not found"
    except Exception as e:
        logger.error(f"Error analyzing vaccine document: {str(e)}")
        return f"Error analyzing document: {str(e)}"