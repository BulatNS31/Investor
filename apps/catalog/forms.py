from django import forms

from .models import Industry

SORT_CHOICES = [
	("name", "По названию"),
	("-created_at", "Сначала новые"),
	("founded_at", "По году основания"),
]


class CompanyFilterForm(forms.Form):
	q = forms.CharField(
		label="Поиск",
		required=False,
		widget=forms.TextInput(
			attrs={
				"placeholder": "Название, ИНН, ОГРН…",
				"class": "form-control",
			}
		),
	)
	industry = forms.ModelChoiceField(
		label="Отрасль",
		required=False,
		queryset=Industry.objects.all(),
		empty_label="Все отрасли",
		to_field_name="slug",
		widget=forms.Select(attrs={"class": "form-select"}),
	)
	sort = forms.ChoiceField(
		label="Сортировка",
		required=False,
		choices=SORT_CHOICES,
		widget=forms.Select(attrs={"class": "form-select"}),
	)
