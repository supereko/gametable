from django.urls import path
from rest_framework import routers

from apps.api.v1.redis_views import manage_item
from apps.api.v1.redis_views import manage_items
from apps.api.v1.views import CardSubTypeView
from apps.api.v1.views import CardTypeView
from apps.api.v1.views import CardView
from apps.api.v1.views import EffectsView
from apps.api.v1.views import ItemTypeView
from apps.api.v1.views import ItemView
from apps.api.v1.views import MonsterView


app_name = 'api'
getters = 'cards_info'

router = routers.DefaultRouter()
router.register('card-type', CardTypeView)
router.register('card-sub-type', CardSubTypeView)
router.register('item-type', ItemTypeView)
router.register('item', ItemView)
router.register('monster', MonsterView)
router.register('card', CardView)
router.register('effect', EffectsView)

urlpatterns = router.urls

urlpatterns_for_redis = [
    path('redis-recs/', manage_items),
    path('redis-rec/<str:key>', manage_item)
]
urlpatterns += urlpatterns_for_redis

