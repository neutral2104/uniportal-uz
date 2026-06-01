from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Min, Max, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import University, Faculty, FavoriteUniversity
from .forms import UniversityForm, FacultyForm, SearchForm

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.profile.role == 'admin')

# ── Public views ──────────────────────────────────────────────────────────────
def home(request):
    featured  = University.objects.filter(is_featured=True)[:6]
    total_uni = University.objects.count()
    total_fac = Faculty.objects.count()
    cities = sorted(
    set(
        city.strip()
        for city in University.objects.values_list('city', flat=True)
        if city
    )
)
    recent    = University.objects.order_by('-created_at')[:4]
    return render(request, 'universities/home.html', {
        'featured': featured, 'total_uni': total_uni,
        'total_fac': total_fac, 'cities': cities, 'recent': recent,
    })

def university_list(request):
    form = SearchForm(request.GET)
    qs   = University.objects.prefetch_related('faculties').annotate(
               fac_count=Count('faculties'),
               min_t=Min('faculties__tuition_usd'),
               min_s=Min('faculties__min_score'),
           )
    if form.is_valid():
        q = form.cleaned_data
        if q.get('q'):
            qs = qs.filter(Q(name__icontains=q['q']) | Q(short_name__icontains=q['q']) |
                           Q(faculties__name__icontains=q['q']) | Q(faculties__field__icontains=q['q'])).distinct()
        if q.get('city'):
            qs = qs.filter(city=q['city'])
        if q.get('uni_type'):
            qs = qs.filter(uni_type=q['uni_type'])
        if q.get('field'):
            qs = qs.filter(faculties__field__icontains=q['field']).distinct()
        if q.get('min_score'):
            qs = qs.filter(faculties__min_score__lte=q['min_score']).distinct()
        if q.get('max_tuition'):
            qs = qs.filter(faculties__tuition_usd__lte=q['max_tuition']).distinct()

    paginator = Paginator(qs, 12)
    page      = paginator.get_page(request.GET.get('page'))
    fav_ids   = set()
    if request.user.is_authenticated:
        fav_ids = set(FavoriteUniversity.objects.filter(user=request.user).values_list('university_id', flat=True))
    return render(request, 'universities/list.html', {
        'page_obj': page, 'form': form, 'fav_ids': fav_ids,
        'total': paginator.count,
    })

def university_detail(request, slug):
    uni      = get_object_or_404(University, slug=slug)
    faculties = uni.faculties.all()
    is_fav   = False
    if request.user.is_authenticated:
        is_fav = FavoriteUniversity.objects.filter(user=request.user, university=uni).exists()
    return render(request, 'universities/detail.html', {
        'uni': uni, 'faculties': faculties, 'is_fav': is_fav,
    })

@login_required
def toggle_favorite(request, uni_id):
    uni = get_object_or_404(University, pk=uni_id)
    obj, created = FavoriteUniversity.objects.get_or_create(user=request.user, university=uni)
    if not created:
        obj.delete()
        return JsonResponse({'status': 'removed'})
    return JsonResponse({'status': 'added'})

# ── Admin CRUD views ──────────────────────────────────────────────────────────
@user_passes_test(is_admin)
def uni_create(request):
    form = UniversityForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        uni = form.save()
        messages.success(request, f"University '{uni.name}' created.")
        return redirect('uni_detail', slug=uni.slug)
    return render(request, 'universities/form.html', {'form': form, 'title': 'Add University'})

@user_passes_test(is_admin)
def uni_edit(request, slug):
    uni  = get_object_or_404(University, slug=slug)
    form = UniversityForm(request.POST or None, request.FILES or None, instance=uni)
    if form.is_valid():
        form.save()
        messages.success(request, "University updated.")
        return redirect('uni_detail', slug=uni.slug)
    return render(request, 'universities/form.html', {'form': form, 'title': 'Edit University', 'uni': uni})

@user_passes_test(is_admin)
def uni_delete(request, slug):
    uni = get_object_or_404(University, slug=slug)
    if request.method == 'POST':
        uni.delete()
        messages.success(request, "University deleted.")
        return redirect('uni_list')
    return render(request, 'universities/confirm_delete.html', {'uni': uni})

@user_passes_test(is_admin)
def faculty_create(request, uni_slug):
    uni  = get_object_or_404(University, slug=uni_slug)
    form = FacultyForm(request.POST or None, initial={'university': uni})
    if form.is_valid():
        form.save()
        messages.success(request, "Faculty added.")
        return redirect('uni_detail', slug=uni.slug)
    return render(request, 'universities/faculty_form.html', {'form': form, 'uni': uni, 'title': 'Add Faculty'})

@user_passes_test(is_admin)
def faculty_edit(request, pk):
    fac  = get_object_or_404(Faculty, pk=pk)
    form = FacultyForm(request.POST or None, instance=fac)
    if form.is_valid():
        form.save()
        messages.success(request, "Faculty updated.")
        return redirect('uni_detail', slug=fac.university.slug)
    return render(request, 'universities/faculty_form.html', {'form': form, 'uni': fac.university, 'title': 'Edit Faculty'})

@user_passes_test(is_admin)
def faculty_delete(request, pk):
    fac = get_object_or_404(Faculty, pk=pk)
    uni_slug = fac.university.slug
    if request.method == 'POST':
        fac.delete()
        messages.success(request, "Faculty removed.")
        return redirect('uni_detail', slug=uni_slug)
    return render(request, 'universities/confirm_delete_faculty.html', {'fac': fac})
