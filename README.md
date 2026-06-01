# 🎓 UniPortal UZ — AI-Powered University Information Management System

A full-stack Django web application providing an intelligent, searchable portal for university admissions in Uzbekistan. Includes AI assistant (OpenAI), CRUD admin, advanced search/filters, user profiles, favorites, and an admin dashboard.

---

## ✨ Features

| Feature | Details |
|---|---|
| 🔐 **Authentication** | Register, login, logout, profile with avatar & DTM score |
| 🏛 **Universities** | 63 universities, 269 programs pre-loaded from CSV |
| 🔍 **Smart Search** | Filter by field, city, type, DTM score, max tuition |
| 🤖 **AI Assistant** | OpenAI-powered chat for admissions advice & recommendations |
| ❤️ **Favorites** | Save universities to personal profile |
| 📊 **Dashboard** | Admin stats: cities, types, most-saved, recent activity |
| ✏️ **Full CRUD** | Admin users can create/edit/delete universities & programs |
| 📱 **Responsive** | Bootstrap 5, mobile-first design |

---

## 🚀 Quick Start (Local)

### 1. Clone & Setup
```bash
git clone <your-repo>
cd uniportal
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and set your values:
#   SECRET_KEY=your-secret-key
#   OPENAI_API_KEY=sk-...   (optional — core features work without it)
#   DATABASE_URL=            (optional — defaults to SQLite)
```

### 3. Database & Data
```bash
python manage.py migrate
python manage.py import_csv          # loads all 269 programs
python manage.py createsuperuser     # create your admin account
```

### 4. Run
```bash
python manage.py runserver
```
Open http://127.0.0.1:8000

**Default admin:** username `admin`, password `admin123` *(change immediately in production!)*

---

## 🌐 Deploy to Render (Free)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New Web Service → Connect repo
3. Render auto-detects `render.yaml` and sets up everything
4. Add env vars in Render dashboard:
   - `SECRET_KEY` → generate a strong secret
   - `OPENAI_API_KEY` → your OpenAI key
   - `DEBUG` → `False`
5. Deploy — the `release` command runs migrations and imports data automatically

---

## 📁 Project Structure

```
uniportal/
├── config/                  # Django settings, urls, wsgi
│   ├── settings.py
│   └── urls.py
├── apps/
│   ├── accounts/            # Auth: register/login/profile + UserProfile model
│   ├── universities/        # University & Faculty CRUD + search
│   ├── ai_assistant/        # OpenAI chat + AIChatHistory model
│   └── dashboard/           # Admin statistics dashboard
├── templates/               # All HTML templates (base + per-app)
├── static/                  # CSS & JS
├── universities.csv         # Pre-loaded dataset (63 unis, 269 programs)
├── manage.py
├── requirements.txt
├── Procfile                 # Render/Heroku deployment
└── render.yaml              # Render infrastructure config
```

---

## 🗄️ Database Models

| Model | App | Description |
|---|---|---|
| `University` | universities | Name, city, type, description, website, ranking |
| `Faculty` | universities | Program, quotas 2024/2025, scores, tuition, deadline |
| `FavoriteUniversity` | universities | User ↔ University M2M relationship |
| `UserProfile` | accounts | Role, DTM score, budget, city, preferred field |
| `AIChatHistory` | ai_assistant | Per-session chat messages (user + assistant) |

---

## 🤖 AI Assistant

The AI assistant uses OpenAI's `gpt-4o-mini` model with a custom system prompt tuned for Uzbekistan university admissions. It can:

- Compare universities and programs
- Check eligibility based on DTM score
- Recommend programs matching budget and preferences
- Explain scholarship options (state grants, WIUT scholarships, etc.)
- Answer general questions about Uzbekistan's higher education system

**Without an API key**, the bot displays a helpful message and directs users to the search page.

---

## 🔑 User Roles

| Role | Capabilities |
|---|---|
| `student` (default) | Search, view, save favorites, use AI chat |
| `admin` | All above + create/edit/delete universities & programs + dashboard |

To promote a user to admin: Django admin → UserProfile → set role to `admin`, or set `is_staff=True`.

---

## ⚙️ Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Django secret key |
| `DEBUG` | ✅ | `True` for dev, `False` for production |
| `DATABASE_URL` | ❌ | PostgreSQL URL (defaults to SQLite) |
| `OPENAI_API_KEY` | ❌ | Enables AI assistant |
| `ALLOWED_HOSTS` | ✅ | Comma-separated list of allowed hosts |

---

## 📊 Dataset

Pre-loaded from `universities.csv`:
- **63 universities** across all regions of Uzbekistan
- **269 academic programs** with full admission details
- Data covers: Tashkent, Samarkand, Bukhara, Fergana, Andijan, Namangan, Navoi, Karshi, Termez, Jizzakh, Gulistan, Urgench, Nukus
- Sources: DTM/uzbmb.uz, my.gov.uz, official university websites

---

## 🛠 Tech Stack

- **Backend:** Django 4.2, Python 3.11+
- **Database:** PostgreSQL (production) / SQLite (development)
- **Frontend:** Bootstrap 5.3, Bootstrap Icons, vanilla JS
- **AI:** OpenAI API (gpt-4o-mini)
- **Deployment:** Render, Gunicorn, WhiteNoise
