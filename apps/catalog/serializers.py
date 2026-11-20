from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from .models import Company, CompanyIndustry, Industry


class IndustrySerializer(serializers.ModelSerializer):
	companies_count = serializers.IntegerField(read_only=True, default=0)

	class Meta:
		model = Industry
		fields = [
			"id",
			"name",
			"slug",
			"description",
			"companies_count",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["slug", "created_at", "updated_at"]


class IndustryBriefSerializer(serializers.Serializer):
	id = serializers.IntegerField()
	name = serializers.CharField()
	slug = serializers.SlugField()


class CompanyIndustryBriefSerializer(IndustryBriefSerializer):
	is_primary = serializers.BooleanField()


class CompanyIndustrySerializer(serializers.ModelSerializer):
	industry = IndustrySerializer(read_only=True)
	industry_id = serializers.PrimaryKeyRelatedField(
		queryset=Industry.objects.all(),
		source="industry",
		write_only=True,
	)

	class Meta:
		model = CompanyIndustry
		fields = ["industry", "industry_id", "is_primary"]


class CompanyListSerializer(serializers.ModelSerializer):
	primary_industry = serializers.SerializerMethodField()

	class Meta:
		model = Company
		fields = [
			"id",
			"name",
			"short_name",
			"slug",
			"logo",
			"website",
			"founded_at",
			"primary_industry",
		]

	@extend_schema_field(IndustryBriefSerializer(allow_null=True))
	def get_primary_industry(self, obj: Company) -> dict[str, Any] | None:
		links = list(obj.industry_links.all())

		if not links:
			return None

		link = next((item for item in links if item.is_primary), links[0])

		return {
			"id": link.industry.id,
			"name": link.industry.name,
			"slug": link.industry.slug,
		}


class CompanyDetailSerializer(serializers.ModelSerializer):
	industries = serializers.SerializerMethodField()
	industry_ids = serializers.PrimaryKeyRelatedField(
		queryset=Industry.objects.all(),
		many=True,
		write_only=True,
		required=False,
	)

	class Meta:
		model = Company
		fields = [
			"id",
			"name",
			"short_name",
			"slug",
			"description",
			"history",
			"logo",
			"website",
			"inn",
			"ogrn",
			"legal_address",
			"headquarters",
			"founded_at",
			"industries",
			"industry_ids",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["slug", "created_at", "updated_at"]

	@extend_schema_field(CompanyIndustryBriefSerializer(many=True))
	def get_industries(self, obj: Company) -> list[dict[str, Any]]:
		return [
			{
				"id": link.industry.id,
				"name": link.industry.name,
				"slug": link.industry.slug,
				"is_primary": link.is_primary,
			}
			for link in obj.industry_links.all()
		]

	def _sync_industries(
		self,
		company: Company,
		industry_ids: list[Industry],
	) -> None:
		existing = {link.industry_id: link for link in company.industry_links.all()}

		target_ids = {industry.pk for industry in industry_ids}

		for industry_id, link in existing.items():
			if industry_id not in target_ids:
				link.delete()

		for industry_id in target_ids - set(existing.keys()):
			CompanyIndustry.objects.create(
				company=company,
				industry_id=industry_id,
				is_primary=False,
			)

	def create(self, validated_data: dict[str, Any]) -> Company:
		industry_ids = validated_data.pop("industry_ids", [])

		company = Company.objects.create(**validated_data)
		self._sync_industries(company, industry_ids)

		return company

	def update(
		self,
		instance: Company,
		validated_data: dict[str, Any],
	) -> Company:
		industry_ids = validated_data.pop("industry_ids", None)

		for attr, value in validated_data.items():
			setattr(instance, attr, value)

		instance.save()

		if industry_ids is not None:
			self._sync_industries(instance, industry_ids)

		return instance
