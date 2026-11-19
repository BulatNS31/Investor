from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTCookieAuthentication(JWTAuthentication):
    """
    Аутентификация через JWT, хранящийся в HttpOnly cookie.
    Сначала пробуем cookie, затем — стандартный заголовок Authorization.
    """

    def authenticate(self, request):
        # 1. Пробуем cookie
        raw_token = request.COOKIES.get(settings.JWT_AUTH_COOKIE)
        if raw_token:
            try:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token
            except (InvalidToken, TokenError):
                # cookie есть, но протух — идём дальше (заголовок или аноним)
                pass

        # 2. Fallback на стандартный Authorization header (для Swagger/curl)
        return super().authenticate(request)
