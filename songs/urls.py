from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlbumViewSet, ArtistViewSet, TagViewSet, SongViewSet, UserSongHistoryView, HeroSlidesViewSet, UserLikedSongView, LatestUserPlaylists, GlobalSearchAPIView, SongSearchView

router = DefaultRouter()
router.register(r'albums', AlbumViewSet)
router.register(r'artists', ArtistViewSet)
router.register(r'tags', TagViewSet)
router.register(r'songs', SongViewSet)
# router.register(r'songs-history', UserSongHistoryViewSet, basename='songs-history')

urlpatterns = [
    path('', include(router.urls)),
    path('get-slides', HeroSlidesViewSet.as_view(), name='get_slides'),
    path('liked-songs', UserLikedSongView.as_view(), name='liked-songs'),
    path('liked-songs/<int:id>', UserLikedSongView.as_view(), name='liked-song-detail'),
    path('songs-history/', UserSongHistoryView.as_view(), name='songs-history'),
    path('latest-playlists', LatestUserPlaylists.as_view(), name='latest-playlists'),
    path('global-search', GlobalSearchAPIView.as_view(), name='global-search'),
    path('filter', SongSearchView.as_view(), name='global-search'),
]
