from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Album, Artist, Tag, Song, UserSongHistory, UserLikedSong, Playlist, PlaylistSong
from .serializers import AlbumSerializer, ArtistSerializer, TagSerializer, SongSerializer, UserSongHistorySerializer, UserLikedSongSerializer, PlaylistSerializer, PlaylistSongSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .filters import SongFilter, ArtistFilter, AlbumFilter, TagFilter
from django.utils.timezone import now
from .functions import get_slides
from django.shortcuts import get_object_or_404
from .paginators import CustomLimitOffsetPagination
from django.db.models import Q, Exists, OuterRef
from rest_framework.decorators import action
from random import randint
from config import CONFIG

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

        just_get = request.query_params.get('justget') == 'true'

        if user.is_authenticated and not just_get:
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

        if not just_get:
            song.count += 1
            song.save()
        response = super().retrieve(request, *args, **kwargs)
        
        if liked is not None:
            response.data['liked'] = liked
        
        return response
    
    @action(detail=False, methods=['get'])
    def random(self, request):
        count = self.queryset.count()
        if count == 0:
            return Response({"detail": "No songs available"}, status=404)
        
        user = request.user
        index = randint(0, count - 1)
        song = self.queryset.only('id')[index]
        
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
        
        serializer = self.get_serializer(song)

        response = serializer.data
        response['index'] = index
        
        if liked is not None:
            response['liked'] = liked
        
        return Response(response)

    @action(detail=True, methods=['get'])
    def related_songs(self, request, pk=None):
        song = self.get_object()

        related_songs = Song.objects.filter(album=song.album).exclude(id=song.id)

        artist_ids = song.song_artists.values_list('artist_id', flat=True)
        if artist_ids:
            related_songs = related_songs | Song.objects.filter(song_artists__artist_id__in=artist_ids).exclude(id=song.id)

        if (len(related_songs) < 25):
            tag_ids = song.song_tags.values_list('tag_id', flat=True)
            if tag_ids:
                related_songs = related_songs | Song.objects.filter(song_tags__tag_id__in=tag_ids).exclude(id=song.id)

        related_songs = related_songs.distinct().order_by('-count')[:24]

        serializer = self.get_serializer(related_songs, many=True)
        return Response(serializer.data)


class PlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Playlist.objects.none()  # Return an empty queryset if user is not authenticated

        playlists = self.request.user.playlists.all()

        # Check if a song_id is provided in the query params
        song_id = self.request.query_params.get('song_id')
        if song_id:
            playlists = playlists.annotate(
                contains_song=Exists(
                    PlaylistSong.objects.filter(playlist=OuterRef('id'), song_id=song_id)
                )
            )

        return playlists

    def create(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        name = request.data.get('name')
        privacy_type = request.data.get('privacy_type', 'Private')
        songs_id = request.data.get('songs_id')

        if not songs_id or not isinstance(songs_id, list) or len(songs_id) == 0:
            return Response(
                {"error": "songs_id is required and must contain at least one song ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not name:
            return Response(
                {"error": "Playlist name is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        songs = Song.objects.filter(id__in=songs_id)
        songs_ordered = sorted(songs, key=lambda song: songs_id.index(song.id))
        if songs.count() != len(songs_id):
            return Response(
                {"error": "One or more song IDs are invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        playlist = Playlist.objects.create(
            user=request.user,
            name=name,
            privacy_type=privacy_type
        )

        PlaylistSong.objects.bulk_create([
            PlaylistSong(playlist=playlist, song=song) for song in songs_ordered
        ])

        serializer = self.get_serializer(playlist)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def songs(self, request, pk=None):
        playlist = self.get_object()

        if playlist.privacy_type == "Private":
            if not request.user.is_authenticated or playlist.user != request.user:
                return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        paginator = CustomLimitOffsetPagination()
        paginated_songs = paginator.paginate_queryset(playlist.playlist_songs.all(), request)
        serializer = PlaylistSongSerializer(paginated_songs, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data["playlist"] = PlaylistSerializer(playlist).data
        return paginated_response
    
    @action(detail=True, methods=['post'])
    def add_songs(self, request, pk=None):
        """ Adds songs to an existing playlist """
        playlist = self.get_object()

        if playlist.user != request.user:
            return Response({"error": "You do not have permission to modify this playlist."}, status=status.HTTP_403_FORBIDDEN)

        songs_id = request.data.get('songs_id')
        if not songs_id or not isinstance(songs_id, list) or len(songs_id) == 0:
            return Response(
                {"error": "songs_id is required and must contain at least one song ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        songs = Song.objects.filter(id__in=songs_id)
        songs_ordered = sorted(songs, key=lambda song: songs_id.index(song.id))

        if songs.count() != len(songs_id):
            return Response(
                {"error": "One or more song IDs are invalid."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Add songs without checking for duplicates
        PlaylistSong.objects.bulk_create([
            PlaylistSong(playlist=playlist, song=song) for song in songs_ordered
        ])
        return Response({"message": "Songs added successfully."}, status=status.HTTP_200_OK)

class PlaylistSeekerViewSet(viewsets.ModelViewSet):
    serializer_class = PlaylistSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Playlist.objects.none()  # Return an empty queryset if user is not authenticated

        playlists = Playlist.objects.filter(Q(privacy_type='Public') | Q(user=self.request.user))
        return playlists
    
    @action(detail=True, methods=['get'])
    def random(self, request, pk=None):
        user = request.user
        playlist = self.get_object()

        if playlist.privacy_type == "Private" and playlist.user != request.user:
            return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        count = playlist.playlist_songs.count()
        index = randint(0, count - 1)
        playlist_song = playlist.playlist_songs.only('id')[index]
        song = playlist_song.song
        serializer = PlaylistSongSerializer(playlist_song)

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

        if liked is not None:
            serializer.data["song"]["liked"] = liked
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def songs(self, request, pk=None):
        playlist = self.get_object()

        if playlist.privacy_type == "Private":
            if not request.user.is_authenticated or playlist.user != request.user:
                return Response({"error": "Access denied."}, status=status.HTTP_403_FORBIDDEN)

        paginator = CustomLimitOffsetPagination()
        paginated_songs = paginator.paginate_queryset(playlist.playlist_songs.all(), request)
        serializer = PlaylistSongSerializer(paginated_songs, many=True)
        paginated_response = paginator.get_paginated_response(serializer.data)
        paginated_response.data["playlist"] = PlaylistSerializer(playlist).data
        return paginated_response
    
    @action(detail=True, methods=['get'])
    def seek(self, request, pk=None):
        """Efficiently get the next and previous songs in a playlist."""
        playlist = self.get_object()
        playlistsong_id = request.query_params.get('playlistsong_id')
        loop = request.query_params.get('loop')

        current_playlistsong = None
        next_song = None
        prev_song = None

        if (playlistsong_id):
            try:
                current_playlistsong = playlist.playlist_songs.get(id=playlistsong_id)
            except PlaylistSong.DoesNotExist:
                return Response({"error": "Song not found in playlist."}, status=status.HTTP_404_NOT_FOUND)

        if (current_playlistsong):
            next_song = playlist.playlist_songs.filter(id__gt=current_playlistsong.id).order_by('id').first()
            prev_song = playlist.playlist_songs.filter(id__lt=current_playlistsong.id).order_by('-id').first()
        else:
            next_song = playlist.playlist_songs.first()

        if (loop):
            if (prev_song == None):
                prev_song = playlist.playlist_songs.last()
            if (next_song == None):
                next_song = playlist.playlist_songs.first()

        data = {
            "previous_song": PlaylistSongSerializer(prev_song).data if prev_song else None,
            "current_song": PlaylistSongSerializer(current_playlistsong).data if current_playlistsong else None,
            "next_song": PlaylistSongSerializer(next_song).data if next_song else None
        }

        return Response(data, status=status.HTTP_200_OK)




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
            total_songs = playlist.playlist_songs.count()
            if (total_songs):
                response_data.append({
                    "id": playlist.id,
                    "name": playlist.name,
                    "privacy_type": playlist.privacy_type,
                    "songs_count": playlist.playlist_songs.count(),
                    "thumbnail": playlist.playlist_songs.first().song.album.thumbnail300x300,
                })
        return Response(response_data)
    
class GlobalSearchAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        query = request.query_params.get('q', '')
        limit = CONFIG["GLOBAL_SEARCH_LIMIT"]

        if not query:
            return Response({'error': 'Query parameter "q" is required.'}, status=400)

        # Initialize an empty set to track used song IDs
        used_song_ids = set()

        # Search in user history and get unique song IDs
        user_histories = user.song_history.filter(
            Q(song__original_name__icontains=query) |
            Q(song__album__title__icontains=query) |
            Q(song__song_artists__artist__name__icontains=query) |
            Q(song__song_tags__tag__name__icontains=query)
        ).select_related('song__album').prefetch_related('song__song_artists__artist').distinct()[:limit+1]
        used_song_ids.update(user_histories.values_list('song_id', flat=True))

        # Search in songs, excluding already used song IDs
        songs = Song.objects.filter(
            Q(title__icontains=query) |
            Q(lyrics__icontains=query) |
            Q(album__title__icontains=query) |
            Q(song_artists__artist__name__icontains=query) | 
            Q(song_tags__tag__name__icontains=query) 
        ).exclude(id__in=used_song_ids).select_related('album').prefetch_related('song_artists__artist').distinct()[:limit]
        used_song_ids.update(songs.values_list('id', flat=True))

        # Search in user liked songs, excluding already used song IDs
        user_liked_songs = user.liked_songs.filter(
            Q(song__original_name__icontains=query) |
            Q(song__album__title__icontains=query) |
            Q(song__song_artists__artist__name__icontains=query) |
            Q(song__song_tags__tag__name__icontains=query)
        ).exclude(song_id__in=used_song_ids).select_related('song__album').prefetch_related('song__song_artists__artist').distinct()[:limit]
        used_song_ids.update(user_liked_songs.values_list('song_id', flat=True))

        # Search for artists
        artists = Artist.objects.filter(Q(name__icontains=query)).distinct()[:limit]

        # Search for albums
        albums = Album.objects.filter(Q(title__icontains=query)).distinct()[:limit]

        # Search for playlists
        playlists = Playlist.objects.filter(Q(name__icontains=query) & (Q(privacy_type='Public') | Q(user=user))).distinct()[:limit]
        
        # search for tags
        tags = Tag.objects.filter(Q(name__icontains=query)).distinct()[:limit]

        # Serialize results
        data = {
            'user_history': UserSongHistorySerializer(user_histories, many=True).data,
            'songs': SongSerializer(songs, many=True).data,
            'user_liked_songs': UserLikedSongSerializer(user_liked_songs, many=True).data,
            'artists': ArtistSerializer(artists, many=True).data,
            'albums': AlbumSerializer(albums, many=True).data,
            'playlists': PlaylistSerializer(playlists, many=True).data,
            'tags': TagSerializer(tags, many=True).data,
        }

        return Response(data)
    
class SongSearchView(APIView):
    def get(self, request, *args, **kwargs):
        q = request.query_params.get('q', '').strip()
        searchby = request.query_params.get('searchby', '1')
        sortby = request.query_params.get('sortby', '1')
        songs = Song.objects.all()

        if q:
            if searchby == '1':
                songs = songs.filter(original_name__icontains=q)
            elif searchby == '2':
                songs = songs.filter(song_artists__artist__name__icontains=q).distinct()
            elif searchby == '3':
                songs = songs.filter(album__title__icontains=q)
            elif searchby == '4':
                songs = songs.filter(song_tags__tag__name__icontains=q)
            elif searchby == '5':
                if q.isdigit():
                    songs = songs.filter(album__year=int(q))
                else:
                    return Response({"error": "q must be a number for searchby=5"}, status=400)

        if sortby == '1':
            # songs = songs.order_by('-liked_count')
            songs = songs.order_by('-id')
        elif sortby == '2':
            songs = songs.order_by('-count')
        elif sortby == '3':
            songs = songs.order_by('-album__year')

        paginator = CustomLimitOffsetPagination()
        paginated_songs = paginator.paginate_queryset(songs, request)

        serializer = SongSerializer(paginated_songs, many=True)
        return paginator.get_paginated_response(serializer.data)
