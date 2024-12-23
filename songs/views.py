from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Album, Artist, Tag, Song, UserSongHistory, UserLikedSong, Playlist
from .serializers import AlbumSerializer, ArtistSerializer, TagSerializer, SongSerializer, UserSongHistorySerializer, UserLikedSongSerializer, PlaylistSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import SongFilter, ArtistFilter, AlbumFilter, TagFilter
from django.utils.timezone import now
from .functions import get_slides
from django.shortcuts import get_object_or_404
from .paginators import CustomLimitOffsetPagination
from django.db.models import Q

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
    
class GlobalSearchAPIView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        limit = 4

        if not query:
            return Response({'error': 'Query parameter "q" is required.'}, status=400)

        # Initialize an empty set to track used song IDs
        used_song_ids = set()

        # Search in user history and get unique song IDs
        user_histories = UserSongHistory.objects.filter(
            Q(song__original_name__icontains=query) |
            Q(song__album__title__icontains=query) |
            Q(song__song_artists__artist__name__icontains=query)
        ).select_related('song__album').prefetch_related('song__song_artists__artist').distinct()[:limit]
        used_song_ids.update(user_histories.values_list('song_id', flat=True))

        # Search in songs, excluding already used song IDs
        songs = Song.objects.filter(
            Q(title__icontains=query) |
            Q(lyrics__icontains=query) |
            Q(album__title__icontains=query) |
            Q(song_artists__artist__name__icontains=query)
        ).exclude(id__in=used_song_ids).select_related('album').prefetch_related('song_artists__artist').distinct()[:limit]
        used_song_ids.update(songs.values_list('id', flat=True))

        # Search in user liked songs, excluding already used song IDs
        user_liked_songs = UserLikedSong.objects.filter(
            Q(song__original_name__icontains=query) |
            Q(song__album__title__icontains=query) |
            Q(song__song_artists__artist__name__icontains=query)
        ).exclude(song_id__in=used_song_ids).select_related('song__album').prefetch_related('song__song_artists__artist').distinct()[:limit]
        used_song_ids.update(user_liked_songs.values_list('song_id', flat=True))

        # Search for artists
        artists = Artist.objects.filter(Q(name__icontains=query)).distinct()[:limit]

        # Search for albums
        albums = Album.objects.filter(Q(title__icontains=query)).distinct()[:limit]

        # Search for playlists
        playlists = Playlist.objects.filter(Q(name__icontains=query)).distinct()[:limit]

        # Serialize results
        data = {
            'user_history': UserSongHistorySerializer(user_histories, many=True).data,
            'songs': SongSerializer(songs, many=True).data,
            'user_liked_songs': UserLikedSongSerializer(user_liked_songs, many=True).data,
            'artists': ArtistSerializer(artists, many=True).data,
            'albums': AlbumSerializer(albums, many=True).data,
            'playlists': PlaylistSerializer(playlists, many=True).data,
        }

        return Response(data)