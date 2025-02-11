from django.urls import path
from .views import share_song

urlpatterns = [
    path("content/songs/<int:id>", share_song),
]