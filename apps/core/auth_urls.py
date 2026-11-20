from django.urls import path

from apps.core.uploads import ImageUploadView

from .auth_views import (
	CookieLogoutView,
	CookieTokenObtainPairView,
	CookieTokenRefreshView,
	MeView,
)

urlpatterns = [
	path("uploads/image/", ImageUploadView.as_view(), name="image-upload"),
	path("login/", CookieTokenObtainPairView.as_view(), name="auth-login"),
	path("refresh/", CookieTokenRefreshView.as_view(), name="auth-refresh"),
	path("logout/", CookieLogoutView.as_view(), name="auth-logout"),
	path("me/", MeView.as_view(), name="auth-me"),
]
