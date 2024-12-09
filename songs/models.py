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
        # Save the instance to generate the ID
        super().save(*args, **kwargs)
        filename = f"{self.album.code} - {self.original_name}.mp3" 
        # Set the lyrics field after the save
        self.lyrics = f"lrc/{self.id}.lrc"
        file_path = f'songs-file/{filename}'
        encoded_url = urllib.parse.quote(file_path)
        self.url = encoded_url
        self.title = filename

        # Save the instance again to update the lyrics field
        super().save(*args, **kwargs)

class SongArtist(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_artists')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='song_artists')

class SongTag(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='song_tags')

class UserSongHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='song_history')
    song = models.ForeignKey('Song', on_delete=models.CASCADE, related_name='user_history')
    accessed_at = models.DateTimeField(default=now)
    count = models.PositiveBigIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'song'], name='unique_user_song_history')
        ]
        ordering = ['-accessed_at']
