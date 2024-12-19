from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlbumViewSet, ArtistViewSet, TagViewSet, SongViewSet, UserSongHistoryViewSet, HeroSlidesViewSet

router = DefaultRouter()
router.register(r'albums', AlbumViewSet)
router.register(r'artists', ArtistViewSet)
router.register(r'tags', TagViewSet)
router.register(r'songs', SongViewSet)
router.register(r'songs-history', UserSongHistoryViewSet, basename='songs-history')

urlpatterns = [
    path('', include(router.urls)),
    path('get-slides', HeroSlidesViewSet.as_view(), name='get_slides'),
]
