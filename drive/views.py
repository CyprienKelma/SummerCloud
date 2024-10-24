from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import FileUploadForm, FolderCreateForm
from django.http import HttpResponseRedirect
from .models import Folder, File
import os


# Create your views here.
def landing_page(request):
    return render(request, 'landing_page.html')


def signup(request):
    # Dès que le formulaire a été soumis
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Sauvegarde l'utilisateur

            # Créer un dossier personnel pour cet utilisateur dans 'media/'
            user_directory = os.path.join(settings.MEDIA_ROOT, f'user_{user.id}')
            # Si le dossier n'existe pas, on le crée maintenant
            if not os.path.exists(user_directory):
                os.makedirs(user_directory)

            login(request, user)  # Connexion auto dès qu'on est inscrit
            return redirect('user_files')  # Redirection après inscription
    else:
        # Sinon, on affiche le formulaire d'inscription
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def user_files(request):
    user_directory = os.path.join(settings.MEDIA_ROOT, f'user_{request.user.id}')

    # Fichiers du user
    files = os.listdir(user_directory) if os.path.exists(user_directory) else []

    return render(request, 'user_files.html', {'files': files})



def custom_logout(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return render(request, 'landing_page.html')


@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.owner = request.user  # def le user connecté comme propriétaire de son fichier
            file_instance.size = request.FILES['file'].size  # Calcul la taille du fichier (en octets)
            file_instance.name = request.FILES['file'].name
            file_instance.folder = form.cleaned_data['folder'] # Dossier dans lequel le fichier doit être enregistré
            file_instance.save()
            return redirect('user_files')  # Redirection après succès
    else:
        # Passe la liste des dossiers de l'utilisateur pour afficher un choix de dossier
        user_folders = Folder.objects.filter(owner=request.user)
        form = FileUploadForm()
    return render(request, 'manage/upload_file.html', {'form': form, 'folders': user_folders})


@login_required
def create_folder(request):
    if request.method == 'POST':
        form = FolderCreateForm(request.POST)
        if form.is_valid():
            folder_instance = form.save(commit=False)
            folder_instance.owner = request.user  # def le user comme propriétaire du dossier
            folder_instance.save()
            return redirect('user_files')  # Redirection après succès
    else:
        form = FolderCreateForm()
    return render(request, 'manage/create_folder.html', {'form': form})


# Affiche les fichiers et dossiers du user
@login_required
def user_files(request, folder_id=None):
    if folder_id:
        # get le dossier courant
        current_folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    else:
        # Si aucun dossier spécifié => on est à la racine du drive de l'utilisateur
        current_folder = None

    # Sous-dossiers dans le dossier courant (ou dossier racine racine si pas de dossier courant)
    folders = Folder.objects.filter(parent_folder=current_folder, owner=request.user)

    # Fichiers du dossier courant (ou dossier racine si pas de sous dossier)
    files = File.objects.filter(folder=current_folder, owner=request.user)

    # Render la page avec les fichiers et dossiers du user
    return render(request, 'user_files.html', {
        'current_folder': current_folder,
        'folders': folders,
        'files': files,
    })


@login_required
def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id, owner=request.user)
    file.delete()
    messages.success(request, "Fichier supprimé avec succès.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))

@login_required
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    folder.delete()
    messages.success(request, "Dossier supprimé avec succès.")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))