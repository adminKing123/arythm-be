from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin panel
    path('content/', include('songs.urls')),  # Include the URLs from the songs app
    path('auth/', include('accounts.urls')),  # Include the URLs from the songs app
    path('song-requests/', include('songrequest.urls')),  # Include the URLs from the songs app
    path('share/', include('share.urls')),  # Include the URLs from the songs app
]
