from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken
from django.http import JsonResponse
from .models import MTTB_REVOKED_SESSIONS
import jwt

class ForceLogoutMiddleware(MiddlewareMixin):
    """
    Middleware to check if a user's token has been revoked
    """
    def process_request(self, request):
        # Skip for paths that don't require authentication
        exempt_paths = ['/api/login/', '/api/register/', '/admin/', '/static/']
        if any(request.path.startswith(path) for path in exempt_paths):
            return None
        
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        try:
            token = auth_header.split(' ')[1]
            # Decode without verification to get JTI quickly
            payload = jwt.decode(token, options={"verify_signature": False})
            jti = payload.get('jti')
            
            if jti and MTTB_REVOKED_SESSIONS.objects.filter(jti=jti).exists():
                return JsonResponse({
                    'error': 'Your session has been terminated. Please login again.',
                    'code': 'FORCE_LOGOUT'
                }, status=401)
                
        except Exception:
            # If any error occurs, let the normal authentication handle it
            pass
        
        return None