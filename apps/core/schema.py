from typing import Any

from django.conf import settings
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class JWTCookieAuthenticationScheme(OpenApiAuthenticationExtension):
	target_class = "apps.core.authentication.JWTCookieAuthentication"
	name = ["jwtCookieAuth", "jwtBearerAuth"]

	def get_security_definition(self, auto_schema: Any) -> list[dict[str, str]]:
		return [
			{
				"type": "apiKey",
				"in": "cookie",
				"name": settings.JWT_AUTH_COOKIE,
			},
			{
				"type": "http",
				"scheme": "bearer",
				"bearerFormat": "JWT",
			},
		]
