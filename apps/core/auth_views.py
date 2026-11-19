from django.conf import settings
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class CookieTokenObtainPairView(TokenObtainPairView):
    """Логин: ставит access и refresh в HttpOnly cookies."""

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Успешный логин, cookie установлены"),
            401: OpenApiResponse(description="Неверные учётные данные"),
        },
        description="Аутентификация по username/password. Токены устанавливаются в HttpOnly cookies.",
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            access = response.data.get("access")
            refresh = response.data.get("refresh")
            if access:
                response.set_cookie(
                    key=settings.JWT_AUTH_COOKIE,
                    value=access,
                    max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
                    httponly=True,
                    secure=settings.JWT_AUTH_COOKIE_SECURE,
                    samesite=settings.JWT_AUTH_COOKIE_SAMESITE,
                    path=settings.JWT_AUTH_COOKIE_PATH,
                )
            if refresh:
                response.set_cookie(
                    key=settings.JWT_REFRESH_COOKIE,
                    value=refresh,
                    max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
                    httponly=True,
                    secure=settings.JWT_AUTH_COOKIE_SECURE,
                    samesite=settings.JWT_AUTH_COOKIE_SAMESITE,
                    path=settings.JWT_REFRESH_COOKIE_PATH,
                )
            # Чистим тело ответа — токены не должны светиться в JSON
            response.data = {"detail": "Login successful"}
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """Обновление access token из refresh cookie."""

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Access token обновлён, cookie обновлена"),
            401: OpenApiResponse(description="Refresh token отсутствует или невалиден"),
        },
        description="Обновляет access token, используя refresh token из HttpOnly cookie. Тело запроса не нужно.",
    )
    def post(self, request, *args, **kwargs):
        refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        if not refresh:
            return Response(
                {"detail": "Refresh token not found in cookies."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        request.data["refresh"] = refresh
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            access = response.data.get("access")
            if access:
                response.set_cookie(
                    key=settings.JWT_AUTH_COOKIE,
                    value=access,
                    max_age=int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds()),
                    httponly=True,
                    secure=settings.JWT_AUTH_COOKIE_SECURE,
                    samesite=settings.JWT_AUTH_COOKIE_SAMESITE,
                    path=settings.JWT_AUTH_COOKIE_PATH,
                )
            # Если ROTATE_REFRESH_TOKENS=True — SimpleJWT вернёт новый refresh
            new_refresh = response.data.get("refresh")
            if new_refresh:
                response.set_cookie(
                    key=settings.JWT_REFRESH_COOKIE,
                    value=new_refresh,
                    max_age=int(settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()),
                    httponly=True,
                    secure=settings.JWT_AUTH_COOKIE_SECURE,
                    samesite=settings.JWT_AUTH_COOKIE_SAMESITE,
                    path=settings.JWT_REFRESH_COOKIE_PATH,
                )
            response.data = {"detail": "Token refreshed"}

        return response


class CookieLogoutView(APIView):
    """Логаут: чёрный список refresh и очистка cookies."""

    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: OpenApiResponse(description="Выход выполнен")},
        description="Очищает auth cookies и добавляет refresh token в чёрный список.",
    )
    def post(self, request):
        refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        if refresh:
            try:
                token = RefreshToken(refresh)
                token.blacklist()
            except TokenError:
                pass  # уже протух или невалиден — не страшно

        response = Response({"detail": "Logged out"}, status=status.HTTP_200_OK)
        response.delete_cookie(
            settings.JWT_AUTH_COOKIE,
            path=settings.JWT_AUTH_COOKIE_PATH,
            samesite=settings.JWT_AUTH_COOKIE_SAMESITE,
        )
        response.delete_cookie(
            settings.JWT_REFRESH_COOKIE,
            path=settings.JWT_REFRESH_COOKIE_PATH,
            samesite=settings.JWT_AUTH_COOKIE_SAMESITE,
        )
        return response


class MeView(APIView):
    """Информация о текущем пользователе."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: OpenApiResponse(description="Данные пользователя")},
        description="Возвращает информацию о текущем аутентифицированном пользователе.",
    )
    def get(self, request):
        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "is_staff": request.user.is_staff,
            }
        )
