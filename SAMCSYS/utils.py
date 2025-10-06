from decimal import Decimal
from django.db import models, transaction
from django.utils import timezone
from django.db.models import F
import time
import random
import logging

logger = logging.getLogger(__name__)

class JournalEntryHelper:
    """Helper class for journal entry operations with race condition prevention"""
   
    @staticmethod
    @transaction.atomic
    def generate_reference_number(module_id, txn_code, date=None, max_retries=5):
        """
        Generate auto reference number with module_id prefix using database locking.
        
        This method uses select_for_update() to prevent race conditions when
        multiple users generate references simultaneously.
        
        Args:
            module_id: Module identifier (e.g., 'GL')
            txn_code: Transaction code
            date: Target date (defaults to today)
            max_retries: Maximum number of retry attempts
            
        Returns:
            str: Generated reference number (e.g., GL-TRF-20250609-0000001)
            
        Raises:
            Exception: If unable to generate reference after max_retries
        """
        from .models import DETB_JRNL_SEQUENCE
        
        if date is None:
            date = timezone.now().date()
       
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')
       
        # New format: MODULE-TXN-YYYYMMDD
        sequence_key = f"{module_id}-{txn_code}-{year}{month}{day}"
        
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    # Use select_for_update() to lock the row
                    # nowait=False means wait for lock to be released
                    sequence_obj, created = DETB_JRNL_SEQUENCE.objects.select_for_update().get_or_create(
                        sequence_key=sequence_key,
                        defaults={'current_sequence': 0}
                    )
                    
                    # Increment the sequence atomically
                    next_seq = sequence_obj.current_sequence + 1
                    sequence_obj.current_sequence = next_seq
                    sequence_obj.save(update_fields=['current_sequence', 'last_updated'])
                    
                    reference_no = f"{sequence_key}-{next_seq:07d}"
                    
                    logger.info(f"Generated reference: {reference_no} (attempt {attempt + 1})")
                    return reference_no
                    
            except Exception as e:
                logger.warning(f"Reference generation attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < max_retries - 1:
                    # Exponential backoff with jitter
                    sleep_time = (0.1 * (2 ** attempt)) + (random.random() * 0.1)
                    time.sleep(sleep_time)
                else:
                    logger.error(f"Failed to generate reference after {max_retries} attempts")
                    raise Exception(
                        f"Unable to generate reference number after {max_retries} attempts. "
                        "Please try again."
                    )
    
    @staticmethod
    def generate_reference_number_fallback(module_id, txn_code, date=None):
        """
        Fallback method using the old approach with added unique timestamp.
        Only used if the sequence table method fails.
        """
        from .models import DETB_JRNL_LOG
        
        if date is None:
            date = timezone.now().date()
       
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')
        
        # Add milliseconds for uniqueness
        timestamp = timezone.now().strftime('%f')[:3]  # milliseconds
       
        date_prefix = f"{module_id}-{txn_code}-{year}{month}{day}"
       
        # Get next sequence number for the day
        latest = DETB_JRNL_LOG.objects.filter(
            Reference_No__startswith=date_prefix
        ).order_by('-Reference_No').first()
       
        if latest:
            try:
                last_seq = int(latest.Reference_No.split('-')[-1])
                next_seq = last_seq + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1
       
        # Add timestamp to ensure uniqueness
        return f"{date_prefix}-{next_seq:07d}-{timestamp}"
   
    @staticmethod
    def validate_balanced_entries(entries):
        """Validate that entries are balanced"""
        total_debit = sum(
            Decimal(str(entry.get('Amount', 0)))
            for entry in entries
            if entry.get('Dr_cr') == 'D'
        )
       
        total_credit = sum(
            Decimal(str(entry.get('Amount', 0)))
            for entry in entries
            if entry.get('Dr_cr') == 'C'
        )
       
        return abs(total_debit - total_credit) < Decimal('0.01')
   
    @staticmethod
    def get_journal_balance(reference_no):
        """Get balance information for a reference number"""
        from .models import DETB_JRNL_LOG
        
        entries = DETB_JRNL_LOG.objects.filter(Reference_No=reference_no)
       
        if not entries.exists():
            return None
       
        totals = entries.aggregate(
            debit_total=models.Sum('lcy_dr'),
            credit_total=models.Sum('lcy_cr')
        )
       
        debit_total = totals['debit_total'] or Decimal('0.00')
        credit_total = totals['credit_total'] or Decimal('0.00')
        difference = debit_total - credit_total
       
        return {
            'reference_no': reference_no,
            'entry_count': entries.count(),
            'debit_total': debit_total,
            'credit_total': credit_total,
            'difference': difference,
            'is_balanced': abs(difference) < Decimal('0.01')
        }
    
    @staticmethod
    def check_reference_exists(reference_no):
        """Check if a reference number already exists"""
        from .models import DETB_JRNL_LOG
        return DETB_JRNL_LOG.objects.filter(Reference_No=reference_no).exists()



