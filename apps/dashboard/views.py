from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from apps.universities.models import University, Faculty, FavoriteUniversity
from apps.ai_assistant.models import AIChatHistory

def is_admin(user):
    return user.is_authenticated and (user.is_staff or (hasattr(user,'profile') and user.profile.role=='admin'))

@user_passes_test(is_admin)
def dashboard(request):
    stats = {
        'total_universities': University.objects.count(),
        'total_faculties':    Faculty.objects.count(),
        'total_users':        User.objects.count(),
        'total_chats':        AIChatHistory.objects.count(),
        'total_favorites':    FavoriteUniversity.objects.count(),
        'featured_unis':      University.objects.filter(is_featured=True).count(),
    }
    stats_list = [
        ('Universities', stats['total_universities'], '🏛', '#1a237e'),
        ('Programs',     stats['total_faculties'],    '📚', '#1b5e20'),
        ('Users',        stats['total_users'],        '👥', '#b71c1c'),
        ('AI Chats',     stats['total_chats'],        '🤖', '#e65100'),
        ('Saved',        stats['total_favorites'],    '❤️', '#880e4f'),
        ('Featured',     stats['featured_unis'],      '⭐', '#f57f17'),
    ]
    by_city  = University.objects.values('city').annotate(n=Count('id')).order_by('-n')[:8]
    by_type  = University.objects.values('uni_type').annotate(n=Count('id'))
    top_fav  = University.objects.annotate(fav=Count('favorited_by')).order_by('-fav')[:5]
    recent_uni   = University.objects.order_by('-created_at')[:5]
    recent_users = User.objects.order_by('-date_joined')[:5]
    by_field = Faculty.objects.values('field').annotate(n=Count('id')).order_by('-n')[:10]

    return render(request, 'dashboard/index.html', {
        'stats': stats, 'stats_list': stats_list,
        'by_city': by_city, 'by_type': by_type,
        'top_fav': top_fav, 'recent_uni': recent_uni,
        'recent_users': recent_users, 'by_field': by_field,
    })
