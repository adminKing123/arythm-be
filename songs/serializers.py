from rest_framework import serializers
from .models import Album, Artist, Tag, Song, SongArtist, SongTag

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
        fields = ['id', 'title', 'url', 'original_name', 'lyrics', 'album', 'tags', 'artists', 'count']

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

