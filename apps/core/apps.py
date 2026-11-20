from django.apps import AppConfig


class CoreConfig(AppConfig):
	default_auto_field = "django.db.models.BigAutoField"
	name = "apps.core"
	label = "core"
	verbose_name = "Ядро приложения"

	def ready(self) -> None:
		from . import schema  # noqa: F401
