from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import TagView, IngredientView, RecipeViewSet

router = DefaultRouter()

router.register('tags', TagView)
router.register('ingredients', IngredientView)
router.register('recipes', RecipeViewSet)

app_name = 'recipe'


urlpatterns = [
    path('', include(router.urls))
]
