from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from .models import MTTB_Users

class MTTBJWTAuthentication(JWTAuthentication):
    """
    Extend the default to look up MTTB_User instead of Django's auth user.
    """
    def get_user(self, validated_token):
        """
        validated_token is the JWT payload after signature/exp check.
        We override this to fetch from MTTB_User.
        """
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise AuthenticationFailed('Token contained no recognizable user identification', 'token_no_user_id')

        try:
            return MTTB_Users.objects.get(pk=user_id)
        except MTTB_Users.DoesNotExist:
            raise AuthenticationFailed('User not found', 'user_not_found')
