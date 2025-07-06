# utils.py
from decimal import Decimal
from django.db import models
from django.utils import timezone
from .models import DETB_JRNL_LOG

class JournalEntryHelper:
    """Helper class for journal entry operations"""
    
    @staticmethod
    def generate_reference_number(module_id, txn_code, date=None):
        """Generate auto reference number with module_id prefix"""
        if date is None:
            date = timezone.now().date()
        
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')
        
        # New format: MODULE-TXN-YYMMDD
        date_prefix = f"{module_id}-{txn_code}-{year}{month}{day}"
        
        # Get next sequence number for the day and module combination
        latest = DETB_JRNL_LOG.objects.filter(
            Reference_No__startswith=date_prefix
        ).order_by('-Reference_No').first()
        
        if latest:
            try:
                # Extract sequence from: GL-TRF-250609-00001
                last_seq = int(latest.Reference_No.split('-')[-1])
                next_seq = last_seq + 1
            except (ValueError, IndexError):
                next_seq = 1
        else:
            next_seq = 1
        
        return f"{date_prefix}-{next_seq:07d}"
    
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