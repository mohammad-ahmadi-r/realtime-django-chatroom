from django.urls import path
from . import views
app_name= "chat"

urlpatterns = [
    path('', views.Index, name="index"),
    path('profile/<str:pk>/', views.profile, name='profile'),
    path('room/<uuid:pk>/', views.privatems, name='privatems'),
    path('editprof/<str:pk>/', views.editprof, name='editprof'),
    path('checkseen/<str:pk>/', views.checkseen, name='checkseen'),
]