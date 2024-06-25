from django.db import models

class Metadata(models.Model):
    slug = models.SlugField(unique=True, null=False)   
    timestamp = models.DateTimeField(unique=False, null=False)
    name=models.CharField(max_length=20,unique=False,default='Untitled')
    author = models.CharField(max_length=30, unique=False, null=False, default='Anonymous') # Optional
    user_agent = models.CharField(max_length=150, unique=False, null=False)
    password=models.CharField(max_length=150, unique=False, null=True)
    key_usages = models.IntegerField(unique=False, null=False, default=0)
    expiry_time=models.DateTimeField(unique=False, null=False)

    def __str__(self):
        return self.slug

    class Meta:
        db_table = 'metadata'

    def is_protected(self):
        return bool(self.password)

    # def compose_key(self):
    #     # Describe the key convention here:
    #     return self.slug 
    
