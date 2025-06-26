from rest_framework_simplejwt.tokens import RefreshToken

class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        token = super().for_user(user)
        
        # Add custom claims
        token['user_name'] = user.user_name
        token['user_email'] = getattr(user, 'user_email', '')
        
        # Add role information
        if hasattr(user, 'Role_ID') and user.Role_ID:
            token['role'] = getattr(user.Role_ID, 'role_name', '')
            
        return token
