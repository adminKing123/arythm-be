from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Album, Artist, Tag, Song, UserSongHistory
from .serializers import AlbumSerializer, ArtistSerializer, TagSerializer, SongSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import SongFilter, ArtistFilter, AlbumFilter, TagFilter
from django.utils.timezone import now
from .functions import get_slides


class AlbumViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AlbumFilter

class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ArtistFilter

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TagFilter

class SongViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Song.objects.all()
    serializer_class = SongSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = SongFilter

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        song = self.get_object()
        if user.is_authenticated:
            user_song_history, created = UserSongHistory.objects.update_or_create(
                user=user,
                song=song,
                defaults={'accessed_at': now()}
            )
            if not created:
                user_song_history.count += 1
            else:
                user_song_history.count = 1
            user_song_history.save()
        song.count += 1
        song.save()
        return super().retrieve(request, *args, **kwargs)
    
class HeroSlidesViewSet(APIView):
    def get(self, request):
        return Response(get_slides(request), status=status.HTTP_200_OK)
