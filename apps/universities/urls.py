from django.urls import path
from . import views

urlpatterns = [
    path('',                              views.home,            name='home'),
    path('universities/',                 views.university_list, name='uni_list'),
    path('universities/create/',          views.uni_create,      name='uni_create'),
    path('universities/<slug:slug>/',     views.university_detail, name='uni_detail'),
    path('universities/<slug:slug>/edit/',   views.uni_edit,     name='uni_edit'),
    path('universities/<slug:slug>/delete/', views.uni_delete,   name='uni_delete'),
    path('universities/<slug:uni_slug>/faculty/add/', views.faculty_create, name='faculty_create'),
    path('faculty/<int:pk>/edit/',        views.faculty_edit,    name='faculty_edit'),
    path('faculty/<int:pk>/delete/',      views.faculty_delete,  name='faculty_delete'),
    path('favorites/<int:uni_id>/toggle/', views.toggle_favorite, name='toggle_fav'),
]
