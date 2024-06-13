from django.db import models

class Metadata(models.Model):
    timestamp = models.DateTimeField(unique=False, null=False)
    user_agent = models.CharField(max_length=150, unique=False, null=False)
    slug = models.SlugField(unique=True, null=False)   
    key_usages = models.IntegerField(unique=False, null=False, default=0)
    author = models.CharField(max_length=30, unique=False, null=False, default='Anonymous') # Optional
    expiry_time=models.DateTimeField(unique=False, null=False)
    password=models.CharField(max_length=150, unique=False, null=True)

    def __str__(self):
        return self.slug

    class Meta:
        db_table = 'metadata'

    def is_protected(self):
        return bool(self.password)

    # def compose_key(self):
    #     # Describe the key convention here:
    #     return self.slug 
    
