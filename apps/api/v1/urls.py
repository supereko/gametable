from rest_framework import routers

from apps.api.v1.views import CardTypeView


app_name = 'api'

router = routers.DefaultRouter()
router.register(r'card-type', CardTypeView)

urlpatterns = router.urls
