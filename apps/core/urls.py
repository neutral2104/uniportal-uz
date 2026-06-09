from django.urls import path
from .views import set_language
urlpatterns = [
    path("set-language/", set_language, name="set_language"),
]
