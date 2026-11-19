from rest_framework.routers import DefaultRouter

from .views import CompanyViewSet, IndustryViewSet

router = DefaultRouter()
router.register("industries", IndustryViewSet, basename="industry")
router.register("companies", CompanyViewSet, basename="company")

urlpatterns = router.urls
