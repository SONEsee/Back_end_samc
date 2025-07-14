

# eod_helpers.py
"""
Helper functions for EOD processing
"""
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

class EODExecutionLogger:
    """Custom logger for EOD execution tracking"""
    
    def __init__(self, execution_id=None):
        self.execution_id = execution_id or f"EOD_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = timezone.now()
        self.steps = []
        
    def log_step(self, function_name, status, message, duration=None):
        """Log a step in the EOD process"""
        step = {
            'timestamp': timezone.now(),
            'function_name': function_name,
            'status': status,  # 'started', 'success', 'failed', 'skipped'
            'message': message,
            'duration': duration
        }
        self.steps.append(step)
        
        # Also log to Django logger
        log_message = f"[{self.execution_id}] {function_name}: {status} - {message}"
        if status == 'failed':
            logger.error(log_message)
        elif status == 'success':
            logger.info(log_message)
        else:
            logger.debug(log_message)
    
    def get_summary(self):
        """Get execution summary"""
        total_duration = timezone.now() - self.start_time
        
        summary = {
            'execution_id': self.execution_id,
            'start_time': self.start_time,
            'total_duration': total_duration,
            'total_steps': len(self.steps),
            'successful_steps': len([s for s in self.steps if s['status'] == 'success']),
            'failed_steps': len([s for s in self.steps if s['status'] == 'failed']),
            'skipped_steps': len([s for s in self.steps if s['status'] == 'skipped']),
            'steps': self.steps
        }
        
        return summary

def format_duration(duration):
    """Format duration for display"""
    if isinstance(duration, timedelta):
        total_seconds = int(duration.total_seconds())
    else:
        total_seconds = int(duration)
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    if hours > 0:
        return f"{hours} ຊົ່ວໂມງ {minutes} ນາທີ {seconds} ວິນາທີ"
    elif minutes > 0:
        return f"{minutes} ນາທີ {seconds} ວິນາທີ"
    else:
        return f"{seconds} ວິນາທີ"

def send_eod_notification(execution_summary, success=True):
    """Send EOD completion notification"""
    try:
        if not EOD_SETTINGS.get('send_notifications', False):
            return
        
        subject = f"EOD ສຳເລັດ - {execution_summary['start_time'].strftime('%Y-%m-%d')}" if success else f"EOD ລົ້ມເຫລວ - {execution_summary['start_time'].strftime('%Y-%m-%d')}"
        
        message_parts = [
            f"Execution ID: {execution_summary['execution_id']}",
            f"ເວລາເລີ່ມ: {execution_summary['start_time'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"ໄລຍະເວລາທັງໝົດ: {format_duration(execution_summary['total_duration'])}",
            f"ຟັງຊັນທັງໝົດ: {execution_summary['total_steps']}",
            f"ສຳເລັດ: {execution_summary['successful_steps']}",
            f"ລົ້ມເຫລວ: {execution_summary['failed_steps']}",
            f"ຂ້າມ: {execution_summary['skipped_steps']}",
            "",
            "ລາຍລະອຽດ:"
        ]
        
        for step in execution_summary['steps']:
            status_emoji = {
                'success': '✅',
                'failed': '❌', 
                'skipped': '⏭️',
                'started': '🔄'
            }.get(step['status'], '❓')
            
            message_parts.append(f"{status_emoji} {step['function_name']}: {step['message']}")
        
        message = "\n".join(message_parts)
        
        # Send email notification (configure SMTP settings in Django settings)
        if hasattr(settings, 'EOD_NOTIFICATION_EMAILS'):
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.EOD_NOTIFICATION_EMAILS,
                fail_silently=True
            )
            
    except Exception as e:
        logger.error(f"Failed to send EOD notification: {str(e)}")

def validate_eod_prerequisites():
    """Validate all prerequisites before starting EOD"""
    issues = []
    
    # Check if any unauthorized journals exist
    from .models import ACTB_DAIRY_LOG
    unauthorized_journals = ACTB_DAIRY_LOG.objects.filter(Auth_Status='U').count()
    if unauthorized_journals > 0:
        issues.append(f"ມີ Journal ທີ່ຍັງບໍ່ອະນຸມັດ: {unauthorized_journals} ລາຍການ")
    
    # Check if EOD functions are properly configured
    from .models import MTTB_EOC_MAINTAIN
    eod_functions = MTTB_EOC_MAINTAIN.objects.filter(eoc_type='EOD')
    if not eod_functions.exists():
        issues.append("ບໍ່ພົບການຕັ້ງຄ່າຟັງຊັນ EOD")
    
    unauthorized_functions = eod_functions.filter(Auth_Status='U').count()
    if unauthorized_functions > 0:
        issues.append(f"ມີຟັງຊັນ EOD ທີ່ຍັງບໍ່ອະນຸມັດ: {unauthorized_functions} ຟັງຊັນ")
    
    # Check disk space (optional)
    import shutil
    try:
        disk_usage = shutil.disk_usage('/')
        free_space_gb = disk_usage.free / (1024**3)
        if free_space_gb < 1:  # Less than 1GB free
            issues.append(f"ພື້ນທີ່ດິສຈຳກັດ: {free_space_gb:.2f} GB")
    except:
        pass  # Skip disk check if not available
    
    return len(issues) == 0, issues

def get_next_sequence_number():
    """Get the next sequence number for EOD functions"""
    from .models import MTTB_EOC_MAINTAIN
    
    max_seq = MTTB_EOC_MAINTAIN.objects.filter(
        eoc_type='EOD'
    ).aggregate(
        max_seq=models.Max('eoc_seq_no')
    )['max_seq']
    
    return (max_seq or 0) + 10  # Increment by 10 to allow insertions

def create_default_eod_functions():
    """Create default EOD functions if they don't exist"""
    from .models import MTTB_EOC_MAINTAIN, MTTB_Function_Desc, STTB_ModulesInfo
    
    # Define default EOD functions
    default_functions = [
        ('EOD_JOURNAL', 'ບັນທຶກ Journal ປະຈຳວັນ', 10),
        ('EOD_BALANCE', 'ຄິດໄລ່ຍອດເງິນ', 20),
        ('EOD_INTEREST', 'ຄິດໄລ່ດອກເບ້ຍ', 30),
        ('EOD_REPORT', 'ສ້າງລາຍງານ', 40),
        ('EOD_BACKUP', 'ສຳຮອງຂໍ້ມູນ', 50),
        ('EOD_NOTIFICATION', 'ສົ່ງແຈ້ງເຕືອນ', 60),
    ]
    
    try:
        # Get or create EOD module
        eod_module, created = STTB_ModulesInfo.objects.get_or_create(
            module='EOD',
            defaults={'module_name': 'End of Day Processing'}
        )
        
        for func_id, description, sequence in default_functions:
            # Create function description if not exists
            function_desc, created = MTTB_Function_Desc.objects.get_or_create(
                function_id=func_id,
                defaults={
                    'description_la': description,
                    'description_en': description,
                    'eod_function': 'Y',
                    'function_order': sequence,
                    'Record_Status': 'Y'
                }
            )
            
            # Create EOC maintain record if not exists
            eoc_maintain, created = MTTB_EOC_MAINTAIN.objects.get_or_create(
                function_id=function_desc,
                eoc_type='EOD',
                defaults={
                    'module_id': eod_module,
                    'eoc_seq_no': sequence,
                    'Record_Status': 'C',  # Default to closed
                    'Auth_Status': 'U',   # Default to unauthorized
                    'Once_Auth': 'N'
                }
            )
            
            if created:
                logger.info(f"Created EOD function: {func_id}")
        
        return True, "ສ້າງຟັງຊັນ EOD ພື້ນຖານສຳເລັດ"
        
    except Exception as e:
        logger.error(f"Error creating default EOD functions: {str(e)}")
        return False, f"ເກີດຂໍ້ຜິດພາດ: {str(e)}"