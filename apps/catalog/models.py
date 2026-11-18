from django.db import models
from django.utils.text import slugify


class Industry(models.Model):
	name = models.CharField("Название", max_length=255)
	slug = models.SlugField("Slug", max_length=255, unique=True,
							allow_unicode=True, blank=True)
	description = models.TextField("Описание", blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = "industries"
		verbose_name = "Отрасль"
		verbose_name_plural = "Отрасли"
		ordering = ["name"]

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			base = slugify(self.name, allow_unicode=True)
			slug, i = base, 1
			while Industry.objects.filter(slug=slug).exists():
				i += 1
				slug = f"{base}-{i}"
			self.slug = slug
		super().save(*args, **kwargs)


class Company(models.Model):
	name = models.CharField("Название", max_length=255)
	short_name = models.CharField("Краткое название", max_length=100,
								  blank=True, null=True)
	slug = models.SlugField("Slug", max_length=255, unique=True,
							allow_unicode=True, blank=True)
	description = models.TextField("Описание", blank=True, null=True)
	history = models.TextField("История", blank=True, null=True)
	logo = models.ImageField("Логотип", upload_to="companies/logos/",
							 max_length=500, blank=True, null=True)
	website = models.URLField("Сайт", max_length=255, blank=True, null=True)
	inn = models.CharField("ИНН", max_length=12, unique=True,
						   blank=True, null=True)
	ogrn = models.CharField("ОГРН", max_length=15, unique=True,
							blank=True, null=True)
	legal_address = models.TextField("Юридический адрес",
									 blank=True, null=True)
	headquarters = models.CharField("Штаб-квартира", max_length=255,
									blank=True, null=True)
	founded_at = models.DateField("Дата основания", blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	industries = models.ManyToManyField(
		Industry,
		through="CompanyIndustry",
		related_name="companies",
		blank=True,
		verbose_name="Отрасли",
	)

	class Meta:
		db_table = "companies"
		verbose_name = "Компания"
		verbose_name_plural = "Компании"
		ordering = ["name"]

	def __str__(self):
		return self.name

	def save(self, *args, **kwargs):
		if not self.slug:
			base = slugify(self.name, allow_unicode=True)
			slug, i = base, 1
			while Company.objects.filter(slug=slug).exists():
				i += 1
				slug = f"{base}-{i}"
			self.slug = slug
		super().save(*args, **kwargs)


class CompanyIndustry(models.Model):
	company = models.ForeignKey(Company, on_delete=models.CASCADE,
								related_name="industry_links")
	industry = models.ForeignKey(Industry, on_delete=models.CASCADE,
								 related_name="company_links")
	is_primary = models.BooleanField("Основная", default=False)

	class Meta:
		db_table = "company_industries"
		verbose_name = "Отрасль компании"
		verbose_name_plural = "Отрасли компаний"
		unique_together = ("company", "industry")

	def __str__(self):
		return f"{self.company} — {self.industry}"
