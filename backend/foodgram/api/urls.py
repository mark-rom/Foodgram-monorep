from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r'tags', views.TagViewSet)
router.register(r'recipes', views.RecipeViewSet, basename='Recipe')
router.register(r'ingredients', views.IngredientViewSet)
router.register(r'users', views.FoodgramUserViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken'))
]

urlpatterns += router.urls
