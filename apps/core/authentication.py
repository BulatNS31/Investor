from typing import Any

from django.conf import settings
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTCookieAuthentication(JWTAuthentication):
	"""
	Аутентификация через JWT, хранящийся в HttpOnly cookie.
	Сначала пробуем cookie, затем — стандартный заголовок Authorization.
	"""

	def authenticate(self, request: Request) -> Any:
		raw_token = request.COOKIES.get(settings.JWT_AUTH_COOKIE)

		if raw_token:
			try:
				validated_token = self.get_validated_token(raw_token.encode("utf-8"))
				return self.get_user(validated_token), validated_token
			except (InvalidToken, TokenError):
				pass

		return super().authenticate(request)
