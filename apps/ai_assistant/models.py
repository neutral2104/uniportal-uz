from django.db import models
from django.contrib.auth.models import User

class AIChatHistory(models.Model):
    user      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats', null=True, blank=True)
    session   = models.CharField(max_length=64, blank=True)
    role      = models.CharField(max_length=10, choices=[('user','user'),('assistant','assistant')])
    content   = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.role}] {self.content[:60]}"
