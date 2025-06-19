from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from SAMCSYS.models import MTTB_REVOKED_SESSIONS

class Command(BaseCommand):
    help = 'Clean up expired revoked sessions'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=2,
            help='Delete revoked sessions older than this many days'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Delete old revoked sessions
        deleted_count, _ = MTTB_REVOKED_SESSIONS.objects.filter(
            revoked_at__lt=cutoff_date
        ).delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully deleted {deleted_count} revoked sessions older than {days} days'
            )
        )