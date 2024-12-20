from typing import Any
from django.contrib import admin
from django.http.request import HttpRequest
from .models import Album, Artist, Tag, Song, SongArtist, SongTag, UserSongHistory, UserLikedSong
from django.utils.safestring import mark_safe
from config import CONFIG
from .admin_forms import SongAdminForm, AlbumAdminForm, ArtistAdminForm

# Register Album model
@admin.register(UserSongHistory)
class UserSongHistoryAdmin(admin.ModelAdmin):
    list_display = ['user__username', 'song__original_name', 'accessed_at', 'count']
    sortable_by = ['accessed_at', 'count']
    readonly_fields = ['user', 'song', 'accessed_at', 'count']

@admin.register(UserLikedSong)
class UserLikedSongAdmin(admin.ModelAdmin):
    list_display = ['user__username', 'song__original_name', 'liked_at']
    sortable_by = ['liked_at']
    readonly_fields = ['user', 'song', 'liked_at']

# Register Album model
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    form = AlbumAdminForm
    list_display = ['code', 'title', 'year', 'custom_thumbnail300x300', 'custom_thumbnail1200x1200']
    search_fields = ['title', 'code']

    def get_fields(self, request, obj=None):
        if obj:  # Editing or viewing an existing Album
            return ['code', 'title', 'year', 'thumbnail300x300', 'thumbnail1200x1200', 'custom_thumbnailpreview']
        else:  # Adding a new Album
            return ['code', 'title', 'year', 'image_file']  # image_file should be included when creating

        
    def get_readonly_fields(self, request, obj):
        if obj:  # Editing or viewing an existing Song
            return ['code', 'title', 'year', 'thumbnail300x300', 'thumbnail1200x1200', 'custom_thumbnailpreview']
        else:  # Adding a new Song
            return ['thumbnail300x300', 'thumbnail1200x1200', 'custom_thumbnailpreview']

    def custom_thumbnail300x300(self, obj):
        # Custom logic for the URL (display as a clickable link)
        link = f'{CONFIG["SRC_URI"]}{obj.thumbnail300x300}'  # Generate the full URL
        return mark_safe(f'<a href="{link}" target="_blank">{obj.title}</a>')
    
    def custom_thumbnail1200x1200(self, obj):
        # Custom logic for the URL (display as a clickable link)
        link = f'{CONFIG["SRC_URI"]}{obj.thumbnail1200x1200}'  # Generate the full URL
        return mark_safe(f'<a href="{link}" target="_blank">{obj.title}</a>')
    
    def custom_thumbnailpreview(self, obj):
        link = f'{CONFIG["SRC_URI"]}{obj.thumbnail300x300}'  # Generate the full URL
        return mark_safe(f'<img src="{link}" alt="{obj.title}" width="300" height="300" style="border: 1px solid var(--border-color);border-radius:4px;" />')
    
    fields = ['code', 'title', 'year', 'thumbnail300x300', 'thumbnail1200x1200', 'custom_thumbnailpreview']
    
    custom_thumbnail300x300.short_description = 'thumbnail300x300'
    custom_thumbnail1200x1200.short_description = 'thumbnail1200x1200'
    custom_thumbnailpreview.short_description = 'Thumbnail Preview'

# Register Artist model
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    form = ArtistAdminForm
    list_display = ['name', 'custom_thumbnail300x300', 'custom_thumbnail1200x1200']
    search_fields = ['name']

    def get_fields(self, request, obj=None):
        if obj:  # Editing or viewing an existing Album
            return ['name', 'thumbnail300x300', 'thumbnail1200x1200', 'custom_thumbnailpreview']
        else:  # Adding a new Album
            return ['name', 'image_file']

        
    def get_readonly_fields(self, request, obj):
        if obj:  # Editing or viewing an existing Song
            return ['name', 'thumbnail300x300', 'thumbnail1200x1200', 'custom_thumbnailpreview']
        else:  # Adding a new Song
            return ['thumbnail300x300', 'thumbnail1200x1200', 'custom_thumbnailpreview']


    def custom_thumbnail300x300(self, obj):
        # Custom logic for the URL (display as a clickable link)
        link = f'{CONFIG["SRC_URI"]}{obj.thumbnail300x300}'  # Generate the full URL
        return mark_safe(f'<a href="{link}" target="_blank">{obj.name}</a>')
    
    def custom_thumbnail1200x1200(self, obj):
        # Custom logic for the URL (display as a clickable link)
        link = f'{CONFIG["SRC_URI"]}{obj.thumbnail1200x1200}'  # Generate the full URL
        return mark_safe(f'<a href="{link}" target="_blank">{obj.name}</a>')
    
    def custom_thumbnailpreview(self, obj):
        link = f'{CONFIG["SRC_URI"]}{obj.thumbnail300x300}'  # Generate the full URL
        return mark_safe(f'<img src="{link}" alt="{obj.name}" width="300" height="300" style="border: 1px solid var(--border-color);border-radius:4px;" />')
    
    custom_thumbnail300x300.short_description = 'thumbnail300x300'
    custom_thumbnail1200x1200.short_description = 'thumbnail1200x1200'
    custom_thumbnailpreview.short_description = 'Thumbnail Preview'

# Register Tag model
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


# Resgister Song model
class SongArtistInline(admin.TabularInline):
    model = SongArtist
    extra = 0  # Number of empty forms to display initially

# Inline for SongTag relationship
class SongTagInline(admin.TabularInline):
    model = SongTag
    extra = 0

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    form = SongAdminForm
    list_display = ['original_name', 'album_name', 'album__year', 'custom_url', 'count', 'liked_count']  # Add 'artist_names' to list_display
    search_fields = ['original_name']
    sortable_by = ['original_name', 'album__year', 'count', 'liked_count']
    inlines = [SongArtistInline, SongTagInline]  # Show SongArtists and SongTags as inlines

    def get_fields(self, request, obj=None):
        if obj:  # Editing or viewing an existing Song
            return ['title', 'original_name', 'album_name', 'custom_lyrics', 'url', 'audio_preview']
        else:  # Adding a new Song
            return ['original_name', 'album', 'mp3_file']
        
    def get_readonly_fields(self, request, obj):
        if obj:  # Editing or viewing an existing Song
            return ['audio_preview', 'custom_lyrics', 'title', 'url', 'original_name', 'album_name', 'count']
        else:  # Adding a new Song
            return ['count', 'liked_count']

    # Custom method to display album name instead of ID
    def album_name(self, obj):
        return mark_safe(f'<a href="/admin/songs/album/{obj.album.id}/change/">{obj.album.title}</a>')
    
    def custom_url(self, obj):
        # Custom logic for the URL (display as a clickable link)
        link = f'{CONFIG["SRC_URI"]}{obj.url}'  # Generate the full URL
        return mark_safe(f'<a href="{link}" target="_blank">{obj.title}</a>')
    
    def audio_preview(self, obj):
        print(f'{CONFIG["SRC_URI"]}{obj.url}')
        return mark_safe(f'<audio controls><source src="{CONFIG["SRC_URI"]}{obj.url}" type="audio/mpeg"></audio>')
    
    def custom_lyrics(self, obj):
        # Custom logic for the URL (display as a clickable link)
        link = f'{CONFIG["SRC_URI"]}{obj.lyrics}'  # Generate the full URL
        return mark_safe(f'<a href="{link}" target="_blank">link</a>')
    
    album_name.admin_order_field = 'album'  # Allow sorting by album
    album_name.short_description = 'Album'  # Set the column header name
    custom_url.short_description = 'URL'  # Set custom header for the URL field
    custom_lyrics.short_description = 'Lyrics'  # Set custom header for the URL field

    # Use a custom form layout to display related artists and tags
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form
