from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.articles.views import (
	ArticleStatusViewSet,
	ArticleViewSet,
	CategoryViewSet,
	TagViewSet,
)
from apps.catalog.views import CompanyViewSet, IndustryViewSet
from apps.core.uploads import ImageUploadView

router = DefaultRouter()
router.register("industries", IndustryViewSet, basename="industry")
router.register("companies", CompanyViewSet, basename="company")
router.register("articles", ArticleViewSet, basename="article")
router.register("categories", CategoryViewSet, basename="category")
router.register("tags", TagViewSet, basename="tag")
router.register("article-statuses", ArticleStatusViewSet, basename="article-status")

urlpatterns = [
	path("", include(router.urls)),
	path("uploads/image/", ImageUploadView.as_view(), name="image-upload"),
]
