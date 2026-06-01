from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import uuid

CITY_CHOICES = [
    ('Tashkent','Tashkent'), ('Samarkand','Samarkand'), ('Bukhara','Bukhara'),
    ('Namangan','Namangan'), ('Andijan','Andijan'), ('Fergana','Fergana'),
    ('Nukus','Nukus'), ('Karshi','Karshi'), ('Termez','Termez'),
    ('Jizzakh','Jizzakh'), ('Gulistan','Gulistan'), ('Navoi','Navoi'),
    ('Urgench','Urgench'), ('Other','Other'),
]

TYPE_CHOICES = [
    ('state','State'), ('private','Private'), ('international','International'),
]

class University(models.Model):
    name          = models.CharField(max_length=255, unique=True)
    slug          = models.SlugField(max_length=255, unique=True, blank=True)
    short_name    = models.CharField(max_length=50, blank=True)
    city          = models.CharField(max_length=50, choices=CITY_CHOICES, default='Tashkent')
    uni_type      = models.CharField(max_length=20, choices=TYPE_CHOICES, default='state')
    description   = models.TextField(blank=True)
    website       = models.URLField(blank=True)
    application_link = models.URLField(blank=True)
    logo          = models.ImageField(upload_to='logos/', blank=True, null=True)
    founded_year  = models.PositiveIntegerField(blank=True, null=True)
    ranking       = models.PositiveIntegerField(blank=True, null=True)
    total_students = models.PositiveIntegerField(blank=True, null=True)
    is_featured   = models.BooleanField(default=False)
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Universities'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def min_tuition(self):
        f = self.faculties.aggregate(models.Min('tuition_usd'))['tuition_usd__min']
        return f

    @property
    def max_tuition(self):
        f = self.faculties.aggregate(models.Max('tuition_usd'))['tuition_usd__max']
        return f

    @property
    def faculty_count(self):
        return self.faculties.count()


class Faculty(models.Model):
    university    = models.ForeignKey(University, on_delete=models.CASCADE, related_name='faculties')
    name          = models.CharField(max_length=255)
    field         = models.CharField(max_length=255)
    quota_2024    = models.PositiveIntegerField(default=0)
    quota_2025    = models.PositiveIntegerField(default=0)
    min_score     = models.PositiveIntegerField(default=0)
    max_score     = models.PositiveIntegerField(default=0)
    tuition_usd   = models.PositiveIntegerField(default=0)
    deadline      = models.DateField(blank=True, null=True)
    requirements  = models.TextField(blank=True)
    duration_years = models.PositiveSmallIntegerField(default=4)
    language      = models.CharField(max_length=100, default='Uzbek/Russian')
    degree_type   = models.CharField(max_length=50, default='Bachelor')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Faculties'
        ordering = ['name']

    def __str__(self):
        return f"{self.university.short_name or self.university.name} — {self.name}"


class FavoriteUniversity(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='favorited_by')
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'university')

    def __str__(self):
        return f"{self.user.username} → {self.university.name}"
