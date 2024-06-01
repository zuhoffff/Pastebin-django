from django.db import models

class Metadata(models.Model):
    timestamp = models.CharField(max_length=150, unique=False, null=False)
    user_agent = models.CharField(max_length=150, unique=False, null=False)
    s3_key = models.CharField(max_length=10, unique=True, null=False)   
    key_usages = models.IntegerField(unique=False, null=False, default=0)
    author = models.CharField(max_length=30, unique=False, null=False, default='Anonymous') # Optional

    def __str__(self):
        return self.timestamp

    class Meta:
        db_table = 'metadata'