from django.db import models
from django.conf import settings

# Create your models here.
class Schools(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=100)
    secondary_phone = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='manager', default=1)
    website = models.URLField(null=True, blank=True)
    logo = models.ImageField(upload_to='schools', null=True, blank=True)

    def __str__(self):
        return self.name


class Teams(models.Model):
    school = models.ForeignKey(Schools, on_delete=models.CASCADE)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='members')
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    captain = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='captain')
    patron = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patron')
    points = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

        
    