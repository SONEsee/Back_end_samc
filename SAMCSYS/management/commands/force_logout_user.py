from django.core.management.base import BaseCommand
from SAMCSYS.models import MTTB_Users, MTTB_USER_ACCESS_LOG, MTTB_REVOKED_SESSIONS
from django.utils import timezone

class Command(BaseCommand):
    help = 'Force logout a user by their ID'
    
    def add_arguments(self, parser):
        parser.add_argument('user_id', type=str, help='User ID to force logout')
        parser.add_argument(
            '--reason',
            type=str,
            default='Force logout via management command',
            help='Reason for force logout'
        )
    
    def handle(self, *args, **options):
        user_id = options['user_id']
        reason = options['reason']
        
        try:
            user = MTTB_Users.objects.get(user_id=user_id)
        except MTTB_Users.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {user_id} not found'))
            return
        
        # Find and revoke all active sessions
        active_sessions = MTTB_USER_ACCESS_LOG.objects.filter(
            user_id=user,
            logout_datetime__isnull=True,
            login_status='S'
        )
        
        revoked_count = 0
        for session in active_sessions:
            if session.session_id:
                MTTB_REVOKED_SESSIONS.objects.get_or_create(
                    jti=session.session_id,
                    defaults={
                        'user_id': user,
                        'reason': reason
                    }
                )
                revoked_count += 1
        
        # Update sessions
        active_sessions.update(
            logout_datetime=timezone.now(),
            logout_type='F',
            remarks=reason
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully force logged out user {user_id}. '
                f'Revoked {revoked_count} tokens.'
            )
        )