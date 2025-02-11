from django.urls import path
from .views import share_song, share_playlist

urlpatterns = [
    path("content/songs/<int:id>", share_song),
    path("content/playlists/<int:id>", share_playlist),
]