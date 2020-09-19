from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TagView

router = DefaultRouter()

router.register('tags', TagView)

app_name = 'recipe'


urlpatterns = [
    path('', include(router.urls))
]
