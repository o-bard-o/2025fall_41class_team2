from rest_framework.authentication import TokenAuthentication
from rest_framework import exceptions

class CookieTokenAuthentication(TokenAuthentication):
    """
    Custom authentication class that reads the auth token from cookies
    instead of the Authorization header.
    """
    def authenticate(self, request):
        # Try to get token from cookie
        token = request.COOKIES.get('auth_token')
        
        if not token:
            return None
        
        return self.authenticate_credentials(token)
