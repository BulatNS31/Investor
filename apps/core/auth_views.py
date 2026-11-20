from datetime import timedelta
from typing import Any, Literal, TypedDict, cast

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

CookieSameSite = Literal["Lax", "Strict", "None", False]


class SimpleJWTSettings(TypedDict):
	ACCESS_TOKEN_LIFETIME: timedelta
	REFRESH_TOKEN_LIFETIME: timedelta


SIMPLE_JWT_CONFIG = cast(
	"SimpleJWTSettings",
	settings.SIMPLE_JWT,
)


def get_cookie_samesite(value: object) -> CookieSameSite:
	allowed_values: tuple[CookieSameSite, ...] = (
		"Lax",
		"Strict",
		"None",
		False,
	)

	if value not in allowed_values:
		raise ImproperlyConfigured(f"Invalid JWT cookie SameSite value: {value!r}")

	return cast("CookieSameSite", value)


def get_access_token_max_age() -> int:
	return int(SIMPLE_JWT_CONFIG["ACCESS_TOKEN_LIFETIME"].total_seconds())


def get_refresh_token_max_age() -> int:
	return int(SIMPLE_JWT_CONFIG["REFRESH_TOKEN_LIFETIME"].total_seconds())


class DetailSerializer(serializers.Serializer):
	"""Простой ответ вида {"detail": "..."}."""

	detail = serializers.CharField()


class MeSerializer(serializers.Serializer):
	"""Ответ MeView."""

	id = serializers.IntegerField()
	username = serializers.CharField()
	email = serializers.EmailField()
	is_staff = serializers.BooleanField()


class CookieTokenObtainPairView(TokenObtainPairView):
	"""Логин: устанавливает access и refresh в HttpOnly cookies."""

	@extend_schema(
		responses={
			200: DetailSerializer,
			401: DetailSerializer,
		},
		description=(
			"Аутентификация по username/password. Токены устанавливаются в HttpOnly cookies."
		),
	)
	def post(
		self,
		request: Request,
		*args: Any,
		**kwargs: Any,
	) -> Response:
		response = super().post(request, *args, **kwargs)

		if response.status_code == status.HTTP_200_OK:
			access = response.data.get("access")
			refresh = response.data.get("refresh")

			if access:
				response.set_cookie(
					key=settings.JWT_AUTH_COOKIE,
					value=access,
					max_age=get_access_token_max_age(),
					httponly=True,
					secure=settings.JWT_AUTH_COOKIE_SECURE,
					samesite=get_cookie_samesite(settings.JWT_AUTH_COOKIE_SAMESITE),
					path=settings.JWT_AUTH_COOKIE_PATH,
				)

			if refresh:
				response.set_cookie(
					key=settings.JWT_REFRESH_COOKIE,
					value=refresh,
					max_age=get_refresh_token_max_age(),
					httponly=True,
					secure=settings.JWT_AUTH_COOKIE_SECURE,
					samesite=get_cookie_samesite(settings.JWT_AUTH_COOKIE_SAMESITE),
					path=settings.JWT_REFRESH_COOKIE_PATH,
				)

			response.data = {"detail": "Login successful"}

		return response


class CookieTokenRefreshView(TokenRefreshView):
	"""Обновление access token из refresh cookie."""

	@extend_schema(
		request=None,
		responses={
			200: DetailSerializer,
			401: DetailSerializer,
		},
		description=(
			"Обновляет access token, используя refresh token "
			"из HttpOnly cookie. Тело запроса не нужно."
		),
	)
	def post(
		self,
		request: Request,
		*args: Any,
		**kwargs: Any,
	) -> Response:
		refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)

		if not refresh:
			return Response(
				{"detail": "Refresh token not found in cookies."},
				status=status.HTTP_401_UNAUTHORIZED,
			)

		serializer = self.get_serializer(data={"refresh": refresh})

		try:
			serializer.is_valid(raise_exception=True)
		except TokenError as exc:
			raise InvalidToken(exc.args[0]) from exc

		data = serializer.validated_data

		response = Response(
			{"detail": "Token refreshed"},
			status=status.HTTP_200_OK,
		)

		access = data.get("access")

		if access:
			response.set_cookie(
				key=settings.JWT_AUTH_COOKIE,
				value=access,
				max_age=get_access_token_max_age(),
				httponly=True,
				secure=settings.JWT_AUTH_COOKIE_SECURE,
				samesite=get_cookie_samesite(settings.JWT_AUTH_COOKIE_SAMESITE),
				path=settings.JWT_AUTH_COOKIE_PATH,
			)

		new_refresh = data.get("refresh")

		if new_refresh:
			response.set_cookie(
				key=settings.JWT_REFRESH_COOKIE,
				value=new_refresh,
				max_age=get_refresh_token_max_age(),
				httponly=True,
				secure=settings.JWT_AUTH_COOKIE_SECURE,
				samesite=get_cookie_samesite(settings.JWT_AUTH_COOKIE_SAMESITE),
				path=settings.JWT_REFRESH_COOKIE_PATH,
			)

		return response


class CookieLogoutView(APIView):
	"""Логаут: добавляет refresh token в blacklist и очищает cookies."""

	permission_classes = [AllowAny]

	@extend_schema(
		request=None,
		responses={200: DetailSerializer},
		description=("Очищает auth cookies и добавляет refresh token в чёрный список."),
	)
	def post(self, request: Request) -> Response:
		refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)

		if refresh:
			try:
				token = RefreshToken(cast("Any", refresh))
				token.blacklist()
			except TokenError:
				pass

		response = Response(
			{"detail": "Logged out"},
			status=status.HTTP_200_OK,
		)

		response.delete_cookie(
			settings.JWT_AUTH_COOKIE,
			path=settings.JWT_AUTH_COOKIE_PATH,
			samesite=get_cookie_samesite(settings.JWT_AUTH_COOKIE_SAMESITE),
		)

		response.delete_cookie(
			settings.JWT_REFRESH_COOKIE,
			path=settings.JWT_REFRESH_COOKIE_PATH,
			samesite=get_cookie_samesite(settings.JWT_AUTH_COOKIE_SAMESITE),
		)

		return response


class MeView(APIView):
	"""Информация о текущем пользователе."""

	permission_classes = [IsAuthenticated]

	@extend_schema(
		responses={200: MeSerializer},
		description=("Возвращает информацию о текущем аутентифицированном пользователе."),
	)
	def get(self, request: Request) -> Response:
		user = request.user

		if not user.is_authenticated:
			return Response(
				{"detail": "Authentication required"},
				status=status.HTTP_401_UNAUTHORIZED,
			)

		return Response(
			{
				"id": user.id,
				"username": user.username,
				"email": user.email,
				"is_staff": user.is_staff,
			}
		)
