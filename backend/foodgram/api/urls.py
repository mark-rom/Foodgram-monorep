from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views

router = DefaultRouter()

router.register(r'tags', views.TagViewSet)
router.register(r'recipes', views.RecipeViewSet)
router.register(r'ingredients', views.IngredientViewSet)
router.register(r'users/(?P<user_id>\d+)/subscribe', views.SubscribtionViewSet)
# router.register(r'recipes/download_shopping_cart/')
# router.register(r'recipes/(?P<recipe_id>\d+)/favorite/')

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]

urlpatterns += router.urls
