from .translations import get_t, LANGUAGES, TRANSLATIONS

def lang_context(request):
    lang = request.session.get("lang", "en")
    if lang not in TRANSLATIONS:
        lang = "en"
    return {
        "t": get_t(lang),
        "current_lang": lang,
        "languages": LANGUAGES,
    }
