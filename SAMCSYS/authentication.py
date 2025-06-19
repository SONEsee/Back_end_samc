# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework_simplejwt.exceptions import AuthenticationFailed
# from .models import MTTB_Users, MTTB_USER_ACCESS_LOG

# class MTTBJWTAuthentication(JWTAuthentication):
#     """
#     Extend the default to look up MTTB_User instead of Django's auth user.
#     """
#     def get_user(self, validated_token):
#         """
#         validated_token is the JWT payload after signature/exp check.
#         We override this to fetch from MTTB_User.
#         """
#         try:
#             user_id = validated_token['user_id']
#         except KeyError:
#             raise AuthenticationFailed('Token contained no recognizable user identification', 'token_no_user_id')

#         try:
#             return MTTB_Users.objects.get(pk=user_id)
#         except MTTB_Users.DoesNotExist:
#             raise AuthenticationFailed('User not found', 'user_not_found')
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken
from .models import MTTB_Users, MTTB_REVOKED_SESSIONS
import logging

logger = logging.getLogger(__name__)

class MTTBJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that checks for revoked tokens.
    This replaces the default JWT blacklist functionality.
    """
    
    def get_validated_token(self, raw_token):
        """
        Validates the token and checks if it's been revoked
        """
        # First, validate the token normally (checks signature, expiry, etc.)
        try:
            validated_token = super().get_validated_token(raw_token)
        except TokenError as e:
            raise AuthenticationFailed(str(e))
        
        # Extract JTI from the token
        try:
            jti = validated_token[api_settings.JTI_CLAIM]
        except KeyError:
            raise AuthenticationFailed('Token has no JTI claim')
        
        # Check if this token has been revoked
        if MTTB_REVOKED_SESSIONS.objects.filter(jti=jti).exists():
            logger.info(f"Attempted to use revoked token with JTI: {jti}")
            raise AuthenticationFailed('Your session has been terminated. Please login again.')
        
        return validated_token
    
    def get_user(self, validated_token):
        """
        Get user from validated token with additional checks
        """
        try:
            user_id = validated_token.get('user_id')
            if not user_id:
                raise AuthenticationFailed('Token contained no recognizable user identification')
        except KeyError:
            raise AuthenticationFailed('Token contained no recognizable user identification')
        
        try:
            user = MTTB_Users.objects.get(pk=user_id)
            
            # Additional check: ensure user is still active
            if hasattr(user, 'User_Status') and user.User_Status != 'E':
                raise AuthenticationFailed('User account is disabled')
            
            # Store the JTI in the request for later use (optional)
            if hasattr(validated_token, 'payload'):
                user._cached_jti = validated_token.get(api_settings.JTI_CLAIM)
                
            return user
            
        except MTTB_Users.DoesNotExist:
            raise AuthenticationFailed('User not found')
        except Exception as e:
            logger.error(f"Error authenticating user {user_id}: {str(e)}")
            raise AuthenticationFailed('Authentication failed')


# Optional: Token generation with custom claims
from rest_framework_simplejwt.tokens import RefreshToken

class CustomRefreshToken(RefreshToken):
    """
    Custom refresh token that adds additional claims
    """
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        
        # Add custom claims
        token['user_name'] = user.user_name
        token['user_email'] = getattr(user, 'user_email', '')
        
        # Add role information if available
        if hasattr(user, 'Role_ID') and user.Role_ID:
            token['role'] = getattr(user.Role_ID, 'role_name', '')
            
        return token


# Utility function to extract JTI from request
def get_jti_from_request(request):
    """
    Extract JTI from the Authorization header
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return None
    
    try:
        token_str = auth_header.split(' ')[1]
        token = AccessToken(token_str)
        return token.get(api_settings.JTI_CLAIM)
    except Exception:
        return None