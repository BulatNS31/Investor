from django.db.models import Q, QuerySet
from rest_framework import viewsets
from rest_framework.permissions import (
	SAFE_METHODS,
	BasePermission,
	IsAdminUser,
)
from rest_framework.serializers import Serializer

from .models import Article, ArticleStatus, Category, Tag
from .serializers import (
	ArticleDetailSerializer,
	ArticleListSerializer,
	ArticleStatusSerializer,
	CategorySerializer,
	TagSerializer,
)


class ArticleStatusViewSet(viewsets.ModelViewSet):
	queryset = ArticleStatus.objects.all()
	serializer_class = ArticleStatusSerializer
	lookup_field = "slug"

	def get_permissions(self) -> list[BasePermission]:
		if self.request.method in SAFE_METHODS:
			return []
		return [IsAdminUser()]


class CategoryViewSet(viewsets.ModelViewSet):
	queryset = Category.objects.all()
	serializer_class = CategorySerializer
	lookup_field = "slug"
	search_fields = ["name", "description"]

	def get_permissions(self) -> list[BasePermission]:
		if self.request.method in SAFE_METHODS:
			return []
		return [IsAdminUser()]


class TagViewSet(viewsets.ModelViewSet):
	queryset = Tag.objects.all()
	serializer_class = TagSerializer
	lookup_field = "slug"
	search_fields = ["name"]

	def get_permissions(self) -> list[BasePermission]:
		if self.request.method in SAFE_METHODS:
			return []
		return [IsAdminUser()]


class ArticleViewSet(viewsets.ModelViewSet):
	lookup_field = "slug"
	search_fields = ["title", "excerpt", "content", "seo_title"]
	ordering_fields = ["published_at", "created_at", "reading_time"]
	ordering = ["-published_at", "-created_at"]

	def get_queryset(self) -> QuerySet[Article]:
		qs = Article.objects.select_related("status").prefetch_related(
			"categories",
			"tags",
			"companies",
			"industries",
		)

		# Не-админам показываем только опубликованные статьи.
		user = self.request.user
		if not (user.is_authenticated and user.is_staff):
			qs = qs.filter(status__slug="published")

		params = self.request.query_params
		if status_slug := params.get("status"):
			qs = qs.filter(status__slug=status_slug)
		if category := params.get("category"):
			qs = qs.filter(categories__slug=category)
		if tag := params.get("tag"):
			qs = qs.filter(tags__slug=tag)
		if company := params.get("company"):
			qs = qs.filter(companies__slug=company)
		if industry := params.get("industry"):
			qs = qs.filter(industries__slug=industry)
		if q := params.get("q"):
			qs = qs.filter(
				Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(content__icontains=q)
			)

		return qs.distinct()

	def get_serializer_class(self) -> type[Serializer]:
		if self.action == "list":
			return ArticleListSerializer
		return ArticleDetailSerializer

	def get_permissions(self) -> list[BasePermission]:
		if self.request.method in SAFE_METHODS:
			return []
		return [IsAdminUser()]
