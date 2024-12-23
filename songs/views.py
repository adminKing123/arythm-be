from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Album, Artist, Tag, Song, UserSongHistory, UserLikedSong
from .serializers import AlbumSerializer, ArtistSerializer, TagSerializer, SongSerializer, UserSongHistorySerializer, UserLikedSongSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import SongFilter, ArtistFilter, AlbumFilter, TagFilter
from django.utils.timezone import now
from .functions import get_slides
from django.shortcuts import get_object_or_404
from .paginators import CustomLimitOffsetPagination

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

        liked = None

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

            liked = user.liked_songs.filter(song=song).exists()
        song.count += 1
        song.save()
        response = super().retrieve(request, *args, **kwargs)
        
        if liked is not None:
            response.data['liked'] = liked
        
        return response

class HeroSlidesViewSet(APIView):
    def get(self, request):
        return Response(get_slides(request), status=status.HTTP_200_OK)
    
class UserLikedSongView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, id=None):
        if id:
            try:
                liked_song = request.user.liked_songs.get(id=int(id))
                serializer = UserLikedSongSerializer(liked_song)
                return Response(serializer.data)
            except ValueError:
                return Response({"detail": "id is required!"}, status=status.HTTP_404_NOT_FOUND)
            except UserLikedSong.DoesNotExist:
                return Response({"detail": "liked song not found!"}, status=status.HTTP_404_NOT_FOUND)

        paginator = CustomLimitOffsetPagination()
        paginated_liked_songs = paginator.paginate_queryset(request.user.liked_songs.all(), request)
        serializer = UserLikedSongSerializer(paginated_liked_songs, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        try:
            song_id = request.data.get('song_id')
            song = get_object_or_404(Song, id=song_id)
            
            if UserLikedSong.objects.filter(user=request.user, song=song).exists():
                return Response({"detail": "Song already liked."}, status=status.HTTP_201_CREATED)
            request.user.liked_songs.create(song=song)
            
            return Response({"detail": "Song liked successfully."}, status=status.HTTP_201_CREATED)
        except ValueError:
            return Response({"detail": "song_id is required!"}, status=status.HTTP_201_CREATED)


    def delete(self, request):
        try:
            song_id = int(request.data.get('song_id'))
            song = get_object_or_404(Song, id=song_id)
            likedSongRecord = request.user.liked_songs.get(song=song)
            likedSongRecord.delete()
            return Response({"detail": "Song removed from liked songs."}, status=status.HTTP_204_NO_CONTENT)
        except ValueError:
            return Response({"detail": "id is required!"}, status=status.HTTP_404_NOT_FOUND)
        except UserLikedSong.DoesNotExist:
            return Response({"detail": "Song not found"}, status=status.HTTP_404_NOT_FOUND)
    
class UserSongHistoryView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        paginator = CustomLimitOffsetPagination()
        paginated_history_songs = paginator.paginate_queryset(request.user.song_history.all(), request)
        serializer = UserLikedSongSerializer(paginated_history_songs, many=True)
        return paginator.get_paginated_response(serializer.data)

    def delete(self, request):
        try:
            id = int(request.data.get('id'))
            historySongRecord = request.user.song_history.get(id=id)
            historySongRecord.delete()
            return Response({"detail": "Song removed from history songs."}, status=status.HTTP_204_NO_CONTENT)
        except ValueError:
            return Response({"detail": "id is required!"}, status=status.HTTP_404_NOT_FOUND)
        except UserSongHistory.DoesNotExist:
            return Response({"detail": "Song history not found!"}, status=status.HTTP_404_NOT_FOUND)

class LatestUserPlaylists(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        limit = 12

        response_data = []

        user = request.user
        liked_songs_count = user.liked_songs.count()
        if (liked_songs_count):
            response_data.append({
                "id": "liked_songs",
                "name": "Liked Songs",
                "privacy_type": "Private",
                "songs_count": liked_songs_count,
                "thumbnail": user.liked_songs.first().song.album.thumbnail300x300
            })
            limit-=1

        playlists = user.playlists.all()[:limit]

        for playlist in playlists:
            response_data.append({
                "id": playlist.id,
                "name": playlist.name,
                "privacy_type": playlist.privacy_type,
                "songs_count": playlist.songs.count(),
                "thumbnail": playlist.songs.first().album.thumbnail300x300,
            })
        return Response(response_data)