from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import urllib.parse
from urllib.parse import unquote
from github import Github
from config import CONFIG

class Album(models.Model):
    code = models.CharField(max_length=255, unique=True, null=False)
    title = models.CharField(max_length=255, unique=True, null=False)
    year = models.IntegerField(null=False)
    thumbnail300x300 = models.CharField(max_length=10000, null=False)
    thumbnail1200x1200 = models.CharField(max_length=10000, null=False)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Save the instance to generate the ID
        filename = f'{self.code} - {self.title} ({self.year}).png'
        self.thumbnail300x300 = urllib.parse.quote(f'album-images/300x300/{filename}')
        self.thumbnail1200x1200 = urllib.parse.quote(f'album-images/1200x1200/{filename}')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Extract the file path from the URL field (URL-encoded)
        file_paths = [unquote(self.thumbnail300x300), unquote(self.thumbnail1200x1200)]

        # GitHub API details
        github_token = CONFIG["GITHUB_TOKEN"]
        branch_name = CONFIG["BRANCH_NAME"]
        github_repo_name = CONFIG["GITHUB_REPO_NAME"]
        github = Github(github_token)
        repo = github.get_user().get_repo(github_repo_name)

        for file_path in file_paths:
            try:
                # Get the file from GitHub to confirm it exists
                file_contents = repo.get_contents(file_path, ref=branch_name)

                # Delete the file from GitHub
                repo.delete_file(
                    file_path,  # Path of the file in the repo
                    f"Delete PNG file {self.title}",  # Commit message
                    file_contents.sha,  # SHA of the file to delete
                    branch=branch_name  # Specify the branch to delete from
                )
                print(f"Successfully deleted {file_path} from GitHub.")
            except Exception as e:
                print(f"Failed to delete file {file_path} from GitHub: {e}")

        # Now delete the song instance from the database
        super().delete(*args, **kwargs)

class Artist(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)
    thumbnail300x300 = models.CharField(max_length=10000, null=False)
    thumbnail1200x1200 = models.CharField(max_length=10000, null=False)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Save the instance to generate the ID
        filename = f'{self.name}.png'
        self.thumbnail300x300 = urllib.parse.quote(f'artist-images/300x300/{filename}')
        self.thumbnail1200x1200 = urllib.parse.quote(f'artist-images/1200x1200/{filename}')
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Extract the file path from the URL field (URL-encoded)
        file_paths = [unquote(self.thumbnail300x300), unquote(self.thumbnail1200x1200)]

        # GitHub API details
        github_token = CONFIG["GITHUB_TOKEN"]
        branch_name = CONFIG["BRANCH_NAME"]
        github_repo_name = CONFIG["GITHUB_REPO_NAME"]
        github = Github(github_token)
        repo = github.get_user().get_repo(github_repo_name)

        for file_path in file_paths:
            try:
                # Get the file from GitHub to confirm it exists
                file_contents = repo.get_contents(file_path, ref=branch_name)

                # Delete the file from GitHub
                repo.delete_file(
                    file_path,  # Path of the file in the repo
                    f"Delete PNG file {self.name}",  # Commit message
                    file_contents.sha,  # SHA of the file to delete
                    branch=branch_name  # Specify the branch to delete from
                )
                print(f"Successfully deleted {file_path} from GitHub.")
            except Exception as e:
                print(f"Failed to delete file {file_path} from GitHub: {e}")

        # Now delete the song instance from the database
        super().delete(*args, **kwargs)

class Tag(models.Model):
    name = models.CharField(max_length=255, null=False, unique=True)

    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField(max_length=255, unique=True, null=False)
    url = models.CharField(max_length=10000, null=False)
    original_name = models.CharField(max_length=255, null=False)
    lyrics = models.CharField(max_length=10000, null=False)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='songs')
    count = models.PositiveBigIntegerField(default=0)
    liked_count = models.PositiveBigIntegerField(default=0)
    duration = models.FloatField(default=0, null=True, blank=True)

    class Meta:
        ordering = ['-id']

    def delete(self, *args, **kwargs):
        # Extract the file path from the URL field (URL-encoded)
        file_path = unquote(self.url)

        # GitHub API details
        github_token = CONFIG["GITHUB_TOKEN"]
        branch_name = CONFIG["BRANCH_NAME"]
        github_repo_name = CONFIG["GITHUB_REPO_NAME"]
        github = Github(github_token)
        repo = github.get_user().get_repo(github_repo_name)

        try:
            # Get the file from GitHub to confirm it exists
            file_contents = repo.get_contents(file_path, ref=branch_name)

            # Delete the file from GitHub
            repo.delete_file(
                file_path,  # Path of the file in the repo
                f"Delete MP3 file {self.title}",  # Commit message
                file_contents.sha,  # SHA of the file to delete
                branch=branch_name  # Specify the branch to delete from
            )
            print(f"Successfully deleted {file_path} from GitHub.")
        except Exception as e:
            print(f"Failed to delete file {file_path} from GitHub: {e}")

        # Now delete the song instance from the database
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.pk:
            original = Song.objects.get(pk=self.pk)
            self.url = original.url
        super().save(*args, **kwargs)
        
        if not self.pk or self.url == "":
            filename = f"{self.album.code} - {self.original_name}.mp3"
            self.lyrics = f"lrc/{self.id}.lrc"
            file_path = f'songs-file/{filename}'
            encoded_url = urllib.parse.quote(file_path)
            self.url = encoded_url
            self.title = filename
            super().save(*args, **kwargs)

class SongArtist(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_artists')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='artist_songs')

class SongTag(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='tag_songs')

class UserSongHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='song_history')
    song = models.ForeignKey('Song', on_delete=models.CASCADE, related_name='heard_by_users')
    accessed_at = models.DateTimeField(default=now)
    count = models.PositiveBigIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'song'], name='unique_user_song_history')
        ]
        ordering = ['-accessed_at']

class UserLikedSong(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_songs')
    song = models.ForeignKey('Song', on_delete=models.CASCADE, related_name='liked_by')
    liked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'song')
        ordering = ['-liked_at']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.song.liked_count += 1
            self.song.save(update_fields=['liked_count'])
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.song.liked_count -= 1
        self.song.save(update_fields=['liked_count'])
        super().delete(*args, **kwargs)

class Playlist(models.Model):
    PRIVACY_CHOICES = [
        ('Private', 'Private'),
        ('Public', 'Public'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    name = models.CharField(max_length=255, null=False)
    privacy_type = models.CharField(max_length=7, choices=PRIVACY_CHOICES, default='Private')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-updated_at']

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='playlist_songs')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_playlists')