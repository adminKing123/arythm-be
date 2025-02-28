from rest_framework import serializers
from .models import Album, Artist, Tag, Song, UserSongHistory, UserLikedSong, Playlist, PlaylistSong, SongArtist

class AlbumSerializer(serializers.ModelSerializer):

    class Meta:
        model = Album
        fields = ['id', 'code', 'title', 'year', 'thumbnail300x300', 'thumbnail1200x1200']


class ArtistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Artist
        fields = ['id', 'name', 'thumbnail300x300', 'thumbnail1200x1200']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class SongSerializer(serializers.ModelSerializer):
    # Nested serializers for related models
    album = AlbumSerializer()  # Include album data
    tags = TagSerializer(many=True, read_only=True)  # Include multiple tags
    artists = ArtistSerializer(many=True, read_only=True)  # Include multiple artists

    class Meta:
        model = Song
        fields = ['id', 'title', 'url', 'original_name', 'lyrics', 'album', 'tags', 'artists', 'count', 'liked_count', 'duration']

    # To add tags and artists, we need to get them through the related models
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        # Get the related tags by accessing `song_tags` related field (many-to-many relationship)
        tags = instance.song_tags.all()
        representation['tags'] = TagSerializer([tag.tag for tag in tags], many=True).data
        
        # Get the related artists by accessing `song_artists` related field (many-to-many relationship)
        artists = instance.song_artists.all()
        representation['artists'] = ArtistSerializer([artist.artist for artist in artists], many=True).data
        
        return representation

class UserSongHistorySerializer(serializers.ModelSerializer):
    song = SongSerializer()

    class Meta:
        model = UserSongHistory
        fields = ['id', 'song', 'accessed_at', 'count']

class UserLikedSongSerializer(serializers.ModelSerializer):
    song = SongSerializer()

    class Meta:
        model = UserLikedSong
        fields = ['id', 'song', 'liked_at']

class PlaylistSerializer(serializers.ModelSerializer):
    songs_count = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    contains_song = serializers.BooleanField(default=False)  # Default to False if not annotated
    author = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'privacy_type', 'songs_count', 'thumbnail', 'contains_song', 'author']

    def get_songs_count(self, obj):
        return obj.playlist_songs.count()

    def get_thumbnail(self, obj):
        first_song = obj.playlist_songs.first()
        if first_song:
            return first_song.song.album.thumbnail300x300
        return None
    
    def get_author(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username
        }


class PlaylistSongSerializer(serializers.ModelSerializer):
    song = SongSerializer()

    class Meta:
        model = PlaylistSong
        fields = ['id', 'song']

class SongArtistSerializer(serializers.ModelSerializer):
    song = SongSerializer()

    class Meta:
        model = SongArtist
        fields = ['id', 'song']
