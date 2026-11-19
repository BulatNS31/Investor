from django.contrib import admin

from .models import (
    Article,
    ArticleCategory,
    ArticleCompany,
    ArticleIndustry,
    ArticleStatus,
    ArticleTag,
    Category,
    Tag,
)


@admin.register(ArticleStatus)
class ArticleStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class ArticleCategoryInline(admin.TabularInline):
    model = ArticleCategory
    extra = 1
    autocomplete_fields = ["category"]


class ArticleTagInline(admin.TabularInline):
    model = ArticleTag
    extra = 1
    autocomplete_fields = ["tag"]


class ArticleCompanyInline(admin.TabularInline):
    model = ArticleCompany
    extra = 1
    autocomplete_fields = ["company"]


class ArticleIndustryInline(admin.TabularInline):
    model = ArticleIndustry
    extra = 1
    autocomplete_fields = ["industry"]


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "published_at", "reading_time", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    inlines = [
        ArticleCategoryInline,
        ArticleTagInline,
        ArticleCompanyInline,
        ArticleIndustryInline,
    ]
