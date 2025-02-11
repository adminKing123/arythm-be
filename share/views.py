from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from django.http import HttpResponse
from songs.models import Song

from .helpers import is_bot, GET_APP_REDIRECT_URI, make_song_og, GET_SONGS_ARTISTS, GET_SRC_URI, format_time

@api_view(['GET'])
def share_song(request, id):
    if not is_bot(request):
        return redirect(GET_APP_REDIRECT_URI(""))
    song = get_object_or_404(Song, id=id)
    return HttpResponse(make_song_og({
        "title": song.original_name,
        "description": f"{song.album.title} • {song.album.year} • {song.song_artists.first().artist.name} • {format_time(song.duration)}",
        "image": GET_SRC_URI(song.album.thumbnail300x300),
        "url": GET_APP_REDIRECT_URI(f"/song/{id}"),
        "musician": GET_SONGS_ARTISTS(song.song_artists.all()),
        "release_date": song.album.year,
        "duration": song.duration,
    }))