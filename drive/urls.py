from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [

    # Connexion/deconnexion
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='custom_logout'),

    # Inscription
    path('signup/', views.signup, name='signup'),

    # Page de gestion des fichiers
    path('files/', views.user_files, name='user_files'),

    # Page de gestion des fichiers d'un dossier
    path('files/<int:folder_id>/', views.user_files, name='file_manager'),

    # Upload de fichier
    path('upload/', views.upload_file, name='upload_file'),
    # Création d'un dossier
    path('create-folder/', views.create_folder, name='create_folder'),

    # Suppression d'un fichier
    path('delete-file/<int:file_id>/', views.delete_file, name='delete_file'),

    # Suppression d'un dossier
    path('delete-folder/<int:folder_id>/', views.delete_folder, name='delete_folder'),
]
