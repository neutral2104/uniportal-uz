from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

ROLE_CHOICES = [('student','Student'), ('admin','Admin'), ('moderator','Moderator')]

class UserProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role       = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    avatar     = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio        = models.TextField(blank=True)
    phone      = models.CharField(max_length=20, blank=True)
    city       = models.CharField(max_length=100, blank=True)
    dtm_score  = models.PositiveIntegerField(blank=True, null=True, help_text='Your DTM entrance exam score')
    preferred_field = models.CharField(max_length=200, blank=True)
    budget_usd = models.PositiveIntegerField(blank=True, null=True, help_text='Max annual tuition budget USD')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_staff

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
