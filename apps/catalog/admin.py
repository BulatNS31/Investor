from django.contrib import admin

from .models import Company, CompanyIndustry, Industry


class CompanyIndustryInline(admin.TabularInline):
    model = CompanyIndustry
    extra = 1
    autocomplete_fields = ["industry"]


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "short_name", "inn", "ogrn", "founded_at")
    list_filter = ("industries",)
    search_fields = ("name", "short_name", "inn", "ogrn")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CompanyIndustryInline]
