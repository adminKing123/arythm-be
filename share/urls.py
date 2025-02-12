from django.urls import path
from .views import share_song, share_playlist, share_album, share_artist

urlpatterns = [
    path("content/songs/<int:id>", share_song),
    path("content/playlists/<int:id>", share_playlist),
    path("content/albums/<int:id>", share_album),
    path("content/artists/<int:id>", share_artist),
]