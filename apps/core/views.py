from django.http import HttpResponseRedirect
from .translations import TRANSLATIONS

def set_language(request):
    lang = request.POST.get("lang") or request.GET.get("lang", "en")
    if lang not in TRANSLATIONS:
        lang = "en"
    request.session["lang"] = lang
    referer = request.META.get("HTTP_REFERER", "/")
    return HttpResponseRedirect(referer)
