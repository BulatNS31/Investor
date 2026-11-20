import math
import re
from typing import Any

import nh3
from django.utils import timezone
from rest_framework import serializers

from apps.catalog.models import Company, Industry
from apps.catalog.serializers import IndustrySerializer

from .models import Article, ArticleStatus, Category, Tag

ALLOWED_TAGS = {
	"p",
	"br",
	"strong",
	"em",
	"u",
	"s",
	"h1",
	"h2",
	"h3",
	"ul",
	"ol",
	"li",
	"blockquote",
	"a",
	"img",
	"table",
	"thead",
	"tbody",
	"tr",
	"th",
	"td",
	"code",
	"pre",
	"hr",
}

ALLOWED_ATTRS = {
	"a": {"href", "title", "target", "rel"},
	"img": {"src", "alt", "title", "width", "height"},
	"code": {"class"},
}


class ArticleStatusSerializer(serializers.ModelSerializer):
	class Meta:
		model = ArticleStatus
		fields = ["id", "name", "slug"]
		read_only_fields = ["slug"]


class CategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = Category
		fields = ["id", "name", "slug", "description"]
		read_only_fields = ["slug"]


class TagSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tag
		fields = ["id", "name", "slug"]
		read_only_fields = ["slug"]


class _SimpleRefSerializer(serializers.Serializer):
	id = serializers.IntegerField()
	name = serializers.CharField()
	slug = serializers.CharField()


class ArticleListSerializer(serializers.ModelSerializer):
	status = ArticleStatusSerializer(read_only=True)

	class Meta:
		model = Article
		fields = [
			"id",
			"title",
			"slug",
			"excerpt",
			"cover_image",
			"reading_time",
			"status",
			"published_at",
			"created_at",
		]


class ArticleDetailSerializer(serializers.ModelSerializer):
	status = ArticleStatusSerializer(read_only=True)
	status_id = serializers.PrimaryKeyRelatedField(
		queryset=ArticleStatus.objects.all(),
		source="status",
		write_only=True,
	)
	categories = CategorySerializer(many=True, read_only=True)
	category_ids = serializers.PrimaryKeyRelatedField(
		queryset=Category.objects.all(),
		many=True,
		write_only=True,
		required=False,
	)
	tags = TagSerializer(many=True, read_only=True)
	tag_ids = serializers.PrimaryKeyRelatedField(
		queryset=Tag.objects.all(),
		many=True,
		write_only=True,
		required=False,
	)
	companies = _SimpleRefSerializer(many=True, read_only=True)
	company_ids = serializers.PrimaryKeyRelatedField(
		queryset=Company.objects.all(),
		many=True,
		write_only=True,
		required=False,
	)
	industries = IndustrySerializer(many=True, read_only=True)
	industry_ids = serializers.PrimaryKeyRelatedField(
		queryset=Industry.objects.all(),
		many=True,
		write_only=True,
		required=False,
	)

	class Meta:
		model = Article
		fields = [
			"id",
			"title",
			"slug",
			"excerpt",
			"content",
			"cover_image",
			"reading_time",
			"seo_title",
			"seo_description",
			"status",
			"status_id",
			"categories",
			"category_ids",
			"tags",
			"tag_ids",
			"companies",
			"company_ids",
			"industries",
			"industry_ids",
			"published_at",
			"created_at",
			"updated_at",
		]
		read_only_fields = ["slug", "created_at", "updated_at"]

	def validate_content(self, value: str) -> str:
		return nh3.clean(
			value,
			tags=ALLOWED_TAGS,
			attributes=ALLOWED_ATTRS,
			link_rel="noopener noreferrer",
		)

	def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
		content = attrs.get("content")
		if content and not attrs.get("reading_time"):
			text = re.sub(r"<[^>]+>", " ", content)
			words = len(text.split())
			attrs["reading_time"] = max(1, math.ceil(words / 200))

		status = attrs.get("status", getattr(self.instance, "status", None))
		published_at = attrs.get(
			"published_at",
			getattr(self.instance, "published_at", None),
		)
		if status and status.slug == "published" and not published_at:
			attrs["published_at"] = timezone.now()

		return attrs

	def _sync_m2m(
		self,
		instance: Article,
		field_name: str,
		related_items: Any,
	) -> None:
		if related_items is not None:
			getattr(instance, field_name).set(related_items)

	def create(self, validated_data: dict[str, Any]) -> Article:
		categories = validated_data.pop("category_ids", [])
		tags = validated_data.pop("tag_ids", [])
		companies = validated_data.pop("company_ids", [])
		industries = validated_data.pop("industry_ids", [])

		article = Article.objects.create(**validated_data)

		self._sync_m2m(article, "categories", categories)
		self._sync_m2m(article, "tags", tags)
		self._sync_m2m(article, "companies", companies)
		self._sync_m2m(article, "industries", industries)

		return article

	def update(
		self,
		instance: Article,
		validated_data: dict[str, Any],
	) -> Article:
		categories = validated_data.pop("category_ids", None)
		tags = validated_data.pop("tag_ids", None)
		companies = validated_data.pop("company_ids", None)
		industries = validated_data.pop("industry_ids", None)

		for attr, value in validated_data.items():
			setattr(instance, attr, value)

		instance.save()

		self._sync_m2m(instance, "categories", categories)
		self._sync_m2m(instance, "tags", tags)
		self._sync_m2m(instance, "companies", companies)
		self._sync_m2m(instance, "industries", industries)

		return instance
