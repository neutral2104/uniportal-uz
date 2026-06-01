"""
Management command: python manage.py import_csv
Imports universities.csv into the database.
"""
import csv, os
from django.conf import settings
from datetime import datetime
from django.core.management.base import BaseCommand
from apps.universities.models import University, Faculty

CSV_PATH = os.path.join(settings.BASE_DIR, 'universities.csv')

CITY_MAP = {
    'national university of uzbekistan': 'Tashkent',
    'tashkent': 'Tashkent', 'samarkand': 'Samarkand', 'bukhara': 'Bukhara',
    'namangan': 'Namangan', 'andijan': 'Andijan', 'fergana': 'Fergana',
    'nukus': 'Nukus', 'karshi': 'Karshi', 'termez': 'Termez',
    'jizzakh': 'Jizzakh', 'gulistan': 'Gulistan', 'navoi': 'Navoi',
    'urgench': 'Urgench',
}

def guess_city(name):
    nl = name.lower()
    for key, city in CITY_MAP.items():
        if key in nl:
            return city
    return 'Tashkent'

def guess_type(name):
    nl = name.lower()
    if any(k in nl for k in ['westminster','wiut','turin','inha','msu','ajou','kimyo','webster','nordic','mdis','amity']):
        return 'international'
    if any(k in nl for k in ['international','foreign']):
        return 'international'
    return 'state'

FEATURED = {
    'national university of uzbekistan', 'tashkent university of information technologies',
    'westminster international university in tashkent (wiut)',
    'turin polytechnic university in tashkent', 'inha university in tashkent',
    'university of world economy and diplomacy', 'tashkent medical academy',
    'samarkand state university',
}

class Command(BaseCommand):
    help = 'Import university data from universities.csv'

    def handle(self, *args, **options):
        path = os.path.abspath(CSV_PATH)
        if not os.path.exists(path):
            self.stderr.write(f'CSV not found at {path}')
            return

        created_u = created_f = 0
        with open(path, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                uni_name = row['university'].strip()
                uni, new  = University.objects.get_or_create(
                    name=uni_name,
                    defaults={
                        'short_name': '',
                        'city':       guess_city(uni_name),
                        'uni_type':   guess_type(uni_name),
                        'website':    row.get('application_link','').replace('/apply',''),
                        'application_link': row.get('application_link',''),
                        'is_featured': uni_name.lower() in FEATURED,
                    }
                )
                if new:
                    created_u += 1

                try:
                    deadline = datetime.strptime(row['deadline'], '%Y-%m-%d').date() if row.get('deadline') else None
                except ValueError:
                    deadline = None

                _, fnew = Faculty.objects.get_or_create(
                    university=uni,
                    name=row['field'].strip(),
                    defaults={
                        'field':        row['field'].strip(),
                        'quota_2024':   int(row.get('quota_2024') or 0),
                        'quota_2025':   int(row.get('quota_2025') or 0),
                        'min_score':    int(row.get('min_score') or 0),
                        'max_score':    int(row.get('max_score') or 0),
                        'tuition_usd':  int(row.get('tuition_usd') or 0),
                        'deadline':     deadline,
                        'requirements': row.get('requirements',''),
                    }
                )
                if fnew:
                    created_f += 1

        self.stdout.write(self.style.SUCCESS(
            f'Imported: {created_u} new universities, {created_f} new programs.'
        ))
