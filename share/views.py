from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from django.http import HttpResponse
from songs.models import Song, Playlist, Artist, Album

from .helpers import is_bot, GET_APP_REDIRECT_URI, make_og_tags, GET_SRC_URI, format_time, SHARE_API_MAPS

@api_view(['GET'])
def share_song(request, id):
    redirect_url = SHARE_API_MAPS["SONG"](id)
    if not is_bot(request):
        return redirect(GET_APP_REDIRECT_URI(redirect_url))
    song = get_object_or_404(Song, id=id)
    return HttpResponse(make_og_tags({
        "title": song.original_name,
        "description": f"{song.album.title} • {song.album.year} • {song.song_artists.first().artist.name} • {format_time(song.duration)}",
        "image": GET_SRC_URI(song.album.thumbnail300x300),
        "url": GET_APP_REDIRECT_URI(redirect_url),
        "type": "music.song",
    }))

@api_view(['GET'])
def share_playlist(request, id):
    redirect_url = SHARE_API_MAPS["PLAYLIST"](id)
    if not is_bot(request):
        return redirect(GET_APP_REDIRECT_URI(redirect_url))
    playlist = get_object_or_404(Playlist, id=id)

    first_song = playlist.playlist_songs.first().song
    return HttpResponse(make_og_tags({
        "title": playlist.name,
        "description": f"Playlist • {playlist.playlist_songs.count()} songs • {playlist.privacy_type} • @{playlist.user.username}",
        "image": GET_SRC_URI(first_song.album.thumbnail300x300),
        "url": GET_APP_REDIRECT_URI(redirect_url),
        "type": "music.playlist",
    }))

@api_view(['GET'])
def share_artist(request, id):
    redirect_url = SHARE_API_MAPS["ARTIST"](id)
    if not is_bot(request):
        return redirect(GET_APP_REDIRECT_URI(redirect_url))
    artist = get_object_or_404(Artist, id=id)

    return HttpResponse(make_og_tags({
        "title": artist.name,
        "description": f"Artist • {artist.artist_songs.count()} songs • 0 followers",
        "image": GET_SRC_URI(artist.album.thumbnail300x300),
        "url": GET_APP_REDIRECT_URI(redirect_url),
        "type": "music.artist",
    }))

@api_view(['GET'])
def share_album(request, id):
    redirect_url = SHARE_API_MAPS["ALBUM"](id)
    if not is_bot(request):
        return redirect(GET_APP_REDIRECT_URI(redirect_url))
    album = get_object_or_404(Album, id=id)

    return HttpResponse(make_og_tags({
        "title": album.title,
        "description": f"Album • {album.songs.count()} songs • 0 followers",
        "image": GET_SRC_URI(album.thumbnail300x300),
        "url": GET_APP_REDIRECT_URI(redirect_url),
        "type": "music.album",
    }))
