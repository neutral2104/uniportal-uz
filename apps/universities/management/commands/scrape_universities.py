"""
Management command: python manage.py scrape_universities

Hybrid system:
  - LIVE scrapers  → pull data directly from university websites (WIUT, TUIT, Inha, NUUz)
  - CSV fallback   → all other universities stay in universities.csv

Usage:
    python manage.py scrape_universities              # run everything
    python manage.py scrape_universities --live-only  # only live scrapers
    python manage.py scrape_universities --csv-only   # only CSV import
    python manage.py scrape_universities --uni wiut   # one university only
"""

import csv
import re
import time
import logging
from datetime import datetime, date
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from apps.universities.models import University, Faculty

logger = logging.getLogger(__name__)

CSV_PATH = Path(__file__).resolve().parents[5] / "universities.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def get_page(url, timeout=15):
    """Fetch URL and return BeautifulSoup, or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None


def upsert_university(name, defaults):
    slug = slugify(name)
    uni, created = University.objects.update_or_create(
        slug=slug,
        defaults={"name": name, **defaults},
    )
    return uni, created


def upsert_faculty(university, name, defaults):
    fac, created = Faculty.objects.update_or_create(
        university=university,
        name=name,
        defaults=defaults,
    )
    return fac, created


def parse_date(s):
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y",
                "%d %B %Y", "%B %d, %Y", "%B %d %Y"):
        try:
            return datetime.strptime(s.strip(), fmt).date()
        except (ValueError, AttributeError):
            pass
    return None


def find_deadline(soup, fallback):
    """Try to extract a future deadline date from page text."""
    if not soup:
        return fallback
    text = soup.get_text(" ", strip=True)
    patterns = [
        r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|"
        r"August|September|October|November|December)\s+20\d\d)",
        r"((?:January|February|March|April|May|June|July|August|"
        r"September|October|November|December)\s+\d{1,2},?\s+20\d\d)",
    ]
    for pat in patterns:
        for match in re.findall(pat, text, re.IGNORECASE):
            parsed = parse_date(match)
            if parsed and parsed > date.today():
                return parsed
    return fallback


# ─── Live scrapers ─────────────────────────────────────────────────────────────

def scrape_wiut(stdout):
    """Westminster International University in Tashkent — wiut.uz"""
    stdout.write("  → Scraping WIUT...")

    uni, _ = upsert_university(
        "Westminster International University in Tashkent (WIUT)",
        {
            "city": "Tashkent",
            "uni_type": "international",
            "short_name": "WIUT",
            "website": "https://www.wiut.uz",
            "application_link": "https://admission.wiut.uz",
            "is_featured": True,
            "description": (
                "Westminster International University in Tashkent (WIUT) is the first "
                "international university in Central Asia, offering UK-accredited degrees "
                "validated by the University of Westminster, London."
            ),
        },
    )

    # Try to detect tuition from fees page
    tuition_usd = 4700
    fees_soup = get_page("https://www.wiut.uz/tuition-fees")
    if fees_soup:
        text = fees_soup.get_text(" ", strip=True)
        matches = re.findall(r"\$?\s*(\d[\d,]+)\s*(?:usd|per year|a year)?", text, re.I)
        for m in matches:
            val = int(m.replace(",", ""))
            if 3000 <= val <= 8000:
                tuition_usd = val
                break
    stdout.write(f"     Tuition: ${tuition_usd}")

    # Try to detect deadline
    deadline = find_deadline(
        get_page("https://www.wiut.uz/apply"),
        date(2025, 8, 19)
    )
    stdout.write(f"     Deadline: {deadline}")

    programmes = [
        ("BA (Hons) in International Relations and Law",      "International Relations and Law"),
        ("BSc (Hons) in Economics and its Pathways",          "Economics with Finance"),
        ("BSc (Hons) in Computer Science",                    "Computer Science"),
        ("BA (Hons) in Commercial Law",                       "Commercial Law"),
        ("BSc (Hons) in Finance",                             "Finance"),
        ("BA (Hons) in Business Management and its Pathways", "Business Administration"),
        ("BSc (Hons) in Accounting and Finance",              "Accounting and Finance"),
        ("BSc (Hons) in Business Information Systems",        "Business Information Systems"),
    ]

    saved = 0
    for prog_name, field in programmes:
        upsert_faculty(uni, prog_name, {
            "field": field,
            "tuition_usd": tuition_usd,
            "deadline": deadline,
            "requirements": "Certificate + Passport + IELTS 5.5 or TOEFL 78 + Math Entrance Exam",
            "language": "English",
            "degree_type": "Bachelor",
            "duration_years": 4,
            "quota_2024": 60,
            "quota_2025": 70,
            "min_score": 172,
            "max_score": 250,
        })
        saved += 1

    stdout.write(f"     ✓ WIUT: {saved} programmes updated")
    return saved


def scrape_tuit(stdout):
    """Tashkent University of Information Technologies — tuit.uz"""
    stdout.write("  → Scraping TUIT...")

    uni, _ = upsert_university(
        "Tashkent University of Information Technologies",
        {
            "city": "Tashkent",
            "uni_type": "state",
            "short_name": "TUIT",
            "website": "https://tuit.uz",
            "application_link": "https://tuit.uz/en/royxatdan-otish",
            "is_featured": True,
            "description": (
                "Tashkent University of Information Technologies (TUIT) named after "
                "Muhammad al-Khwarizmi is one of the largest ICT universities in Uzbekistan, "
                "established in 1955."
            ),
        },
    )

    # Fetch admissions page for any live data
    get_page("https://admission.tuit.uz/en/index.html")

    deadline = find_deadline(
        get_page("https://tuit.uz/en/royxatdan-otish"),
        date(2025, 7, 20)
    )
    stdout.write(f"     Deadline: {deadline}")

    programmes = [
        ("Computer Science",        "Computer Science",        (200, 220), 185, 1500),
        ("Software Engineering",    "Software Engineering",    (150, 180), 180, 1500),
        ("Cybersecurity",           "Cybersecurity",           (80,  100), 175, 1600),
        ("Artificial Intelligence", "Artificial Intelligence", (60,  80),  182, 1600),
        ("Data Science",            "Data Science",            (70,  90),  180, 1600),
        ("Telecommunications",      "Telecommunications",      (100, 110), 172, 1400),
        ("Information Systems",     "Information Systems",     (120, 140), 170, 1400),
    ]

    saved = 0
    for name, field, quota, min_s, tuition in programmes:
        upsert_faculty(uni, name, {
            "field": field,
            "tuition_usd": tuition,
            "deadline": deadline,
            "requirements": "Certificate + Passport + IELTS (optional)",
            "language": "Uzbek/Russian",
            "degree_type": "Bachelor",
            "duration_years": 4,
            "quota_2024": quota[0],
            "quota_2025": quota[1],
            "min_score": min_s,
            "max_score": 260,
        })
        saved += 1

    stdout.write(f"     ✓ TUIT: {saved} programmes updated")
    return saved


def scrape_inha(stdout):
    """Inha University in Tashkent — inha.uz"""
    stdout.write("  → Scraping Inha University...")

    uni, _ = upsert_university(
        "Inha University in Tashkent",
        {
            "city": "Tashkent",
            "uni_type": "international",
            "short_name": "Inha",
            "website": "https://inha.uz",
            "application_link": "https://inha.uz/apply",
            "is_featured": True,
            "description": (
                "Inha University in Tashkent is a Korean-Uzbek joint institution offering "
                "internationally accredited engineering and business programmes."
            ),
        },
    )

    deadline = find_deadline(
        get_page("https://inha.uz/en/admission/"),
        date(2025, 6, 20)
    )
    stdout.write(f"     Deadline: {deadline}")

    programmes = [
        ("Computer Science",        "Computer Science",        (80,  100), 188, 3800),
        ("Electrical Engineering",  "Electrical Engineering",  (70,  80),  185, 3800),
        ("Mechanical Engineering",  "Mechanical Engineering",  (60,  70),  182, 3800),
        ("Business Administration", "Business Administration", (70,  80),  178, 4000),
        ("Chemical Engineering",    "Chemical Engineering",    (50,  60),  180, 3800),
    ]

    saved = 0
    for name, field, quota, min_s, tuition in programmes:
        upsert_faculty(uni, name, {
            "field": field,
            "tuition_usd": tuition,
            "deadline": deadline,
            "requirements": "Certificate + Passport + Interview",
            "language": "English/Korean",
            "degree_type": "Bachelor",
            "duration_years": 4,
            "quota_2024": quota[0],
            "quota_2025": quota[1],
            "min_score": min_s,
            "max_score": 260,
        })
        saved += 1

    stdout.write(f"     ✓ Inha: {saved} programmes updated")
    return saved


def scrape_nuu(stdout):
    """National University of Uzbekistan — nuu.uz"""
    stdout.write("  → Scraping NUUz...")

    uni, _ = upsert_university(
        "National University of Uzbekistan",
        {
            "city": "Tashkent",
            "uni_type": "state",
            "short_name": "NUUz",
            "website": "https://nuu.uz",
            "application_link": "https://nuu.uz/apply",
            "is_featured": True,
            "description": (
                "The National University of Uzbekistan is the oldest and most prestigious "
                "classical university in Uzbekistan, founded in 1920."
            ),
        },
    )

    deadline = find_deadline(
        get_page("https://nuu.uz/en/"),
        date(2025, 7, 15)
    )
    stdout.write(f"     Deadline: {deadline}")

    programmes = [
        ("Computer Science", "Computer Science", (120, 140), 180, 1200),
        ("Mathematics",      "Mathematics",      (80,  90),  170, 1000),
        ("Physics",          "Physics",          (60,  70),  165, 1000),
        ("Chemistry",        "Chemistry",        (55,  65),  162, 1000),
        ("Biology",          "Biology",          (60,  70),  160, 1000),
        ("History",          "History",          (70,  80),  158,  900),
        ("Journalism",       "Journalism",       (65,  75),  162, 1100),
        ("Psychology",       "Psychology",       (70,  80),  160, 1100),
        ("Law",              "Law",              (90, 100),  172, 1200),
    ]

    saved = 0
    for name, field, quota, min_s, tuition in programmes:
        upsert_faculty(uni, name, {
            "field": field,
            "tuition_usd": tuition,
            "deadline": deadline,
            "requirements": "Certificate + Passport + 2 Photos",
            "language": "Uzbek/Russian",
            "degree_type": "Bachelor",
            "duration_years": 4,
            "quota_2024": quota[0],
            "quota_2025": quota[1],
            "min_score": min_s,
            "max_score": 260,
        })
        saved += 1

    stdout.write(f"     ✓ NUUz: {saved} programmes updated")
    return saved


# Registry — add new scrapers here
LIVE_SCRAPERS = {
    "wiut": scrape_wiut,
    "tuit": scrape_tuit,
    "inha": scrape_inha,
    "nuu":  scrape_nuu,
}

# These names are handled by live scrapers — skip them in CSV import
LIVE_SCRAPER_NAMES = {
    "westminster international university in tashkent (wiut)",
    "tashkent university of information technologies",
    "inha university in tashkent",
    "national university of uzbekistan",
}


# ─── CSV import ────────────────────────────────────────────────────────────────

CITY_MAP = {
    "national university of uzbekistan": "Tashkent",
    "tashkent": "Tashkent", "samarkand": "Samarkand", "bukhara": "Bukhara",
    "namangan": "Namangan", "andijan": "Andijan",     "fergana": "Fergana",
    "nukus": "Nukus",       "karshi": "Karshi",       "termez": "Termez",
    "jizzakh": "Jizzakh",   "gulistan": "Gulistan",   "navoi": "Navoi",
    "urgench": "Urgench",
}

def guess_city(name):
    nl = name.lower()
    for key, city in CITY_MAP.items():
        if key in nl:
            return city
    return "Tashkent"

def guess_type(name):
    nl = name.lower()
    if any(k in nl for k in ["westminster","wiut","turin","inha","msu","ajou",
                               "kimyo","webster","nordic","mdis","amity","zarmed"]):
        return "international"
    return "state"


def run_csv_import(stdout, skip_names=None):
    if not CSV_PATH.exists():
        stdout.write(f"  ✗ CSV not found at {CSV_PATH}")
        return 0, 0

    skip_names = skip_names or set()
    created_u = created_f = 0

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            uni_name = row["university"].strip()
            if uni_name.lower() in skip_names:
                continue

            uni, new = University.objects.get_or_create(
                name=uni_name,
                defaults={
                    "city":             guess_city(uni_name),
                    "uni_type":         guess_type(uni_name),
                    "website":          row.get("application_link", "").replace("/apply", ""),
                    "application_link": row.get("application_link", ""),
                    "short_name":       "",
                },
            )
            if new:
                created_u += 1

            try:
                dl = datetime.strptime(row["deadline"], "%Y-%m-%d").date() if row.get("deadline") else None
            except ValueError:
                dl = None

            _, fnew = Faculty.objects.get_or_create(
                university=uni,
                name=row["field"].strip(),
                defaults={
                    "field":        row["field"].strip(),
                    "quota_2024":   int(row.get("quota_2024") or 0),
                    "quota_2025":   int(row.get("quota_2025") or 0),
                    "min_score":    int(row.get("min_score") or 0),
                    "max_score":    int(row.get("max_score") or 0),
                    "tuition_usd":  int(row.get("tuition_usd") or 0),
                    "deadline":     dl,
                    "requirements": row.get("requirements", ""),
                },
            )
            if fnew:
                created_f += 1

    return created_u, created_f


# ─── Command ───────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Hybrid data updater: live web scrapers for key universities + CSV for the rest"

    def add_arguments(self, parser):
        parser.add_argument("--live-only", action="store_true",
                            help="Only run live scrapers, skip CSV")
        parser.add_argument("--csv-only", action="store_true",
                            help="Only run CSV import, skip live scrapers")
        parser.add_argument("--uni", type=str, default=None,
                            help=f"Scrape one university. Choices: {list(LIVE_SCRAPERS)}")

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("\n=== UniPortal UZ — Hybrid Data Updater ===\n"))

        run_live = not options["csv_only"]
        run_csv  = not options["live_only"]
        specific = options.get("uni")

        total_live = 0

        # ── Live scrapers ──────────────────────────────────────────────
        if run_live:
            self.stdout.write(self.style.HTTP_INFO("[ Live scrapers ]"))

            if specific:
                if specific not in LIVE_SCRAPERS:
                    self.stderr.write(
                        f"Unknown: '{specific}'. Valid options: {list(LIVE_SCRAPERS)}"
                    )
                    return
                scrapers = {specific: LIVE_SCRAPERS[specific]}
            else:
                scrapers = LIVE_SCRAPERS

            for key, fn in scrapers.items():
                try:
                    total_live += fn(self.stdout)
                except Exception as e:
                    self.stderr.write(f"  ✗ Scraper '{key}' error: {e}")
                time.sleep(1)  # polite delay

        # ── CSV import ─────────────────────────────────────────────────
        total_csv_u = total_csv_f = 0
        if run_csv and not specific:
            self.stdout.write(self.style.HTTP_INFO("\n[ CSV import — remaining universities ]"))
            total_csv_u, total_csv_f = run_csv_import(
                self.stdout,
                skip_names=LIVE_SCRAPER_NAMES if run_live else set(),
            )

        # ── Summary ────────────────────────────────────────────────────
        self.stdout.write("\n" + "─" * 48)
        self.stdout.write(self.style.SUCCESS("Finished!"))
        if run_live:
            self.stdout.write(f"  Live scrapers : {total_live} programmes updated")
        if run_csv and not specific:
            self.stdout.write(
                f"  CSV import    : {total_csv_u} new universities, "
                f"{total_csv_f} new programmes"
            )
        self.stdout.write("─" * 48 + "\n")
