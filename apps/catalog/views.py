from django.db.models import Count, QuerySet
from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAdminUser
from rest_framework.serializers import BaseSerializer

from .models import Company, Industry
from .serializers import (
	CompanyDetailSerializer,
	CompanyListSerializer,
	IndustrySerializer,
)


class IndustryViewSet(viewsets.ModelViewSet):
	serializer_class = IndustrySerializer
	lookup_field = "slug"
	search_fields = ["name", "description"]
	ordering_fields = ["name", "created_at"]
	ordering = ["name"]

	def get_queryset(self) -> QuerySet[Industry]:
		return Industry.objects.annotate(companies_count=Count("companies"))

	def get_permissions(self) -> list[BasePermission]:
		if self.request.method in SAFE_METHODS:
			return []
		return [IsAdminUser()]


class CompanyViewSet(viewsets.ModelViewSet):
	lookup_field = "slug"
	search_fields = ["name", "short_name", "inn", "ogrn", "description"]
	ordering_fields = ["name", "founded_at", "created_at"]
	ordering = ["name"]

	def get_queryset(self) -> QuerySet[Company]:
		queryset = Company.objects.prefetch_related("industry_links__industry")

		industry = self.request.query_params.get("industry")

		if industry:
			queryset = queryset.filter(industry_links__industry__slug=industry)

		return queryset

	def get_serializer_class(self) -> type[BaseSerializer]:
		if self.action == "list":
			return CompanyListSerializer
		return CompanyDetailSerializer

	def get_permissions(self) -> list[BasePermission]:
		if self.request.method in SAFE_METHODS:
			return []
		return [IsAdminUser()]
