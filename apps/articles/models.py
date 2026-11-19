from django.db import models
from django.utils.text import slugify

from apps.catalog.models import Company, Industry


class ArticleStatus(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("Slug", max_length=100, unique=True, allow_unicode=True, blank=True)

    class Meta:
        db_table = "article_statuses"
        verbose_name = "Статус публикации"
        verbose_name_plural = "Статусы публикаций"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name, allow_unicode=True)
            slug, i = base, 1
            while ArticleStatus.objects.filter(slug=slug).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField("Название", max_length=255)
    slug = models.SlugField("Slug", max_length=255, unique=True, allow_unicode=True, blank=True)
    description = models.TextField("Описание", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "categories"
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name, allow_unicode=True)
            slug, i = base, 1
            while Category.objects.filter(slug=slug).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("Slug", max_length=100, unique=True, allow_unicode=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tags"
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name, allow_unicode=True)
            slug, i = base, 1
            while Tag.objects.filter(slug=slug).exists():
                i += 1
                slug = f"{base}-{i}"
            self.slug = slug
        super().save(*args, **kwargs)


class Article(models.Model):
    status = models.ForeignKey(
        ArticleStatus,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="Статус",
    )
    title = models.CharField("Заголовок", max_length=500)
    slug = models.SlugField("Slug", max_length=255, unique=True, allow_unicode=True, blank=True)
    excerpt = models.TextField("Краткое описание", blank=True, null=True)
    content = models.TextField("Содержание", blank=True, null=True)
    cover_image = models.ImageField(
        "Обложка", upload_to="articles/covers/", max_length=500, blank=True, null=True
    )
    reading_time = models.PositiveIntegerField("Время чтения, мин", blank=True, null=True)
    seo_title = models.CharField("SEO Title", max_length=255, blank=True, null=True)
    seo_description = models.TextField("SEO Description", blank=True, null=True)
    published_at = models.DateTimeField("Опубликовано", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    categories = models.ManyToManyField(
        Category,
        through="ArticleCategory",
        related_name="articles",
        blank=True,
        verbose_name="Категории",
    )
    tags = models.ManyToManyField(
        Tag,
        through="ArticleTag",
        related_name="articles",
        blank=True,
        verbose_name="Теги",
    )
    companies = models.ManyToManyField(
        Company,
        through="ArticleCompany",
        related_name="articles",
        blank=True,
        verbose_name="Компании",
    )
    industries = models.ManyToManyField(
        Industry,
        through="ArticleIndustry",
        related_name="articles",
        blank=True,
        verbose_name="Отрасли",
    )

    class Meta:
        db_table = "articles"
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "published_at"], name="articles_index_0"),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title, allow_unicode=True)[:255]
            slug, i = base, 1
            while Article.objects.filter(slug=slug).exists():
                i += 1
                suffix = f"-{i}"
                slug = f"{base[: 255 - len(suffix)]}{suffix}"
            self.slug = slug
        super().save(*args, **kwargs)


class ArticleCategory(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="category_links")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="article_links")

    class Meta:
        db_table = "article_categories"
        verbose_name = "Категория статьи"
        verbose_name_plural = "Категории статей"
        unique_together = ("article", "category")


class ArticleTag(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="tag_links")
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name="article_links")

    class Meta:
        db_table = "article_tags"
        verbose_name = "Тег статьи"
        verbose_name_plural = "Теги статей"
        unique_together = ("article", "tag")


class ArticleCompany(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="company_links")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="article_links")

    class Meta:
        db_table = "article_companies"
        verbose_name = "Компания статьи"
        verbose_name_plural = "Компании статей"
        unique_together = ("article", "company")


class ArticleIndustry(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="industry_links")
    industry = models.ForeignKey(Industry, on_delete=models.CASCADE, related_name="article_links")

    class Meta:
        db_table = "article_industries"
        verbose_name = "Отрасль статьи"
        verbose_name_plural = "Отрасли статей"
        unique_together = ("article", "industry")
