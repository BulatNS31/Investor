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
    """Лёгкая версия для списков — без тяжёлых полей."""

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

    def get_primary_industry(self, obj):
        link = obj.industry_links.filter(is_primary=True).select_related("industry").first()
        if not link:
            link = obj.industry_links.select_related("industry").first()
        if not link:
            return None
        return {"id": link.industry.id, "name": link.industry.name, "slug": link.industry.slug}


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

    def get_industries(self, obj):
        return [
            {
                "id": link.industry.id,
                "name": link.industry.name,
                "slug": link.industry.slug,
                "is_primary": link.is_primary,
            }
            for link in obj.industry_links.select_related("industry").all()
        ]

    def _sync_industries(self, company, industry_ids):
        existing = {link.industry_id: link for link in company.industry_links.all()}
        target_ids = set(industry_ids)

        # удаляем лишние
        for iid, link in existing.items():
            if iid not in target_ids:
                link.delete()

        # добавляем недостающие
        for iid in target_ids - set(existing.keys()):
            CompanyIndustry.objects.create(
                company=company,
                industry_id=iid,
                is_primary=False,
            )

    def create(self, validated_data):
        industry_ids = validated_data.pop("industry_ids", [])
        company = Company.objects.create(**validated_data)
        self._sync_industries(company, industry_ids)
        return company

    def update(self, instance, validated_data):
        industry_ids = validated_data.pop("industry_ids", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if industry_ids is not None:
            self._sync_industries(instance, industry_ids)
        return instance
