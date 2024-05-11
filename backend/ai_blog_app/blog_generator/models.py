from django.db import models
from django.contrib.auth.models import User

# Transcripts Post model
class TranscriptModel(models.Model):
    user                = models.ForeignKey(User, on_delete=models.CASCADE)
    youtube_title       = models.CharField(max_length=300)
    youtube_link        = models.URLField()
    generated_content   = models.CharField(max_length=1000)
    created_at          = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.youtube_title
