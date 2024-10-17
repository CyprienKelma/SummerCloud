from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [

    # Connexion/deconnexion
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),

    # Inscription
    path('signup/', views.signup, name='signup'),

    # Page de gestion des fichiers
    path('user_files/', views.user_files, name='user_files'),
]
