from django.db import models

class Metadata(models.Model):
    timestamp = models.CharField(max_length=20, unique=False, null=False)
    user_agent = models.CharField(max_length=80, unique=False, null=False)
    s3_key = models.CharField(max_length=80, unique=True, null=True)
    key_usages = models.IntegerField(unique=False, null=False, default=0)

    def __str__(self):
        return self.timestamp

    class Meta:
        db_table = 'metadata'