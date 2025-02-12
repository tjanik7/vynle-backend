from django.db import models
from users.models import Account


class Post(models.Model):
    user = models.ForeignKey(Account, related_name='posts', on_delete=models.CASCADE, null=True)
    body = models.TextField(max_length=150)

    # Spotify's unique ID for the release
    spotify_release_uri = models.TextField(max_length=32, blank=True)


class Comment(models.Model):
    body = models.TextField(max_length=150)  # Content of the comment
    user = models.ForeignKey(Account, on_delete=models.CASCADE)  # User who created the comment
    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE)  # Post this comment appears under
