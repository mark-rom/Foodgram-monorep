from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TagViewSet, RecipeViewSet, IngredientViewSet

router = DefaultRouter()

router.register(r'tags', TagViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)
# router.register(r'users/(?P<user_id>\d+)/subscribe', SubscribtionViewSet)

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]

urlpatterns += router.urls
