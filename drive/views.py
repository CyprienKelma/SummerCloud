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
from django.http import JsonResponse
import json
import os
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render
from mimetypes import guess_type


MAX_FILE_SIZE = 1024 * 1024 * 10  # 40 Mo
MAX_STORAGE_SIZE = 1024 * 1024 * 50  # 100 Mo


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




def custom_logout(request):
    logout(request)
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

            # guess-type permet de determiner le type de fichier en fonction de son extension
            mime_type, _ = guess_type(file_instance.name)
            if mime_type:
                if mime_type.startswith('image'):
                    file_instance.type = 'image'
                elif mime_type.startswith('video'):
                    file_instance.type = 'video'
                elif mime_type.startswith('audio'):
                    file_instance.type = 'audio'
                elif mime_type in ['application/pdf', 'application/msword',
                                   'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                    file_instance.type = 'document'
                else:
                    file_instance.type = 'other'
            else:
                file_instance.type = 'other'

            # Enlève les messages d'erreur passé s'il y en a
            storage = messages.get_messages(request)
            storage.used = False

            # Verifie si le fichier est trop gros
            if file_instance.size > MAX_FILE_SIZE:
                messages.error(request, "Désolé, ce fichier est trop volumineux. La taille maximale autorisée est de 40 Mo.")
                return redirect('upload_file')

            # Vérifie qu'ajouter ce fichier ne dépassera pas la limite de stockage totale
            total_storage = sum([file.size for file in File.objects.filter(owner=request.user)]) + file_instance.size
            if total_storage > MAX_STORAGE_SIZE:
                messages.error(request, "Désolé, ce fichier est trop volumineux pour votre drive. "
                                        "Vous avez atteint la limite de stockage de 100 Mo.")
                return redirect('upload_file')


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

    for file in files:
        file.is_pdf = file.file.name.lower().endswith('.pdf')

    # Ficher avec des meta-données en plus pour afficher les informations
    file_types = {
        'image': ['jpg', 'jpeg', 'png', 'gif'],
        'video': ['mp4', 'avi', 'mov', 'mkv'],
        'audio': ['mp3', 'wav', 'flac', 'ogg'],
        'text': ['txt', 'doc', 'docx', 'pdf', 'md'],
        'archive': ['zip', 'rar', 'tar', '7z'],
        'code': ['py', 'js', 'html', 'css', 'java', 'cpp', 'c', 'h', 'hpp', 'cs', 'php', 'rb', 'sh'],
        'spreadsheet': ['xls', 'xlsx', 'ods'],
        'presentation': ['ppt', 'pptx', 'odp'],
        'database': ['sqlite', 'db', 'sql'],
        'executable': ['exe', 'msi', 'deb', 'rpm'],
        'font': ['ttf', 'otf', 'woff', 'woff2'],
        'vector': ['svg', 'ai', 'eps'],
        '3d': ['stl', 'obj', 'fbx', 'blend'],
        'cad': ['dwg', 'dxf'],
        'raster': ['psd', 'ai', 'eps'],
    }
    for file in files:
        extension = file.file.name.split('.')[-1]
        for type, exts in file_types.items():
            if extension in exts:
                file.type = type
                break

    # List qui represente le path des dossiers avec un tuple qui donne le nom et l'id
    path = []
    folder = current_folder
    while folder:
        path.append((folder.name, folder.id))
        folder = folder.parent_folder
    # Inverse la liste pour avoir le path du dossier courant au dossier racine
    path = path[::-1]

    # Render la page avec les fichiers et dossiers du user
    view_format = request.GET.get('view', 'table')
    context = {
        'folders': folders,
        'files': files,
        'path': path,
        'view_format': view_format
    }
    if view_format == 'grid':
        return render(request, 'grid_view.html', context)
    else:
        return render(request, 'table_view.html', context)


@login_required
def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id, owner=request.user)
    file.delete()

    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


@login_required
def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)
    folder.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', 'redirect_if_referer_not_found'))


@login_required
@require_POST
def move_item(request):
    data = json.loads(request.body)
    item_id = data.get("item_id")
    item_type = data.get("item_type") # 'file' ou 'folder'
    destination_folder_id = data.get("destination_folder_id")

    print("Received item_id:", item_id)  # Log de vérification
    print("Received item_type:", item_type)  # Log de vérification
    print("Received destination_folder_id:", destination_folder_id)  # Log de vérification

    try:
        # Vérifie le type d'élément (file ou folder)
        if item_type == "file":
            item = get_object_or_404(File, id=item_id, owner=request.user)
        elif item_type == "folder":
            item = get_object_or_404(Folder, id=item_id, owner=request.user)
        else:
            return JsonResponse({"success": False, "message": "Invalid item type"})

        # Gestion du dossier de destination :
        # Cas où le dossier de destination est le repertoire racine
        if destination_folder_id == "0":
            destination_folder = None
        else:
            # Vérifie si le dossier de destination est correct et appartient à l'utilisateur
            destination_folder = get_object_or_404(Folder, id=destination_folder_id, owner=request.user)

        # On change le dossier parent de l'item par le nv dossier de destination
        item.folder = destination_folder
        item.save()

        return JsonResponse({"success": True})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

def profile(request):
    # Données pour le graphique d'usage du stockagee par le user en fonction du temps
    monthly_usage = (
        File.objects.filter(owner=request.user)
        .annotate(month=TruncMonth('upload_date'))
        .values('month')
        .annotate(total_size=Sum('size'))
        .order_by('month')
    )
    months = [entry['month'].strftime('%Y-%m') for entry in monthly_usage]
    sizes_over_time = [round(entry['total_size'] / (1024 * 1024), 2) for entry in monthly_usage]

    # Données pour le graphique des différents types de fichiers du user
    type_usage = (
        File.objects.filter(owner=request.user)
        .values('type')
        .annotate(total_size=Sum('size'))
        .order_by('type')
    )
    types = [entry['type'] for entry in type_usage]
    sizes_by_type = [round(entry['total_size'] / (1024 * 1024), 2) for entry in type_usage]

    return render(request, 'profile/profile.html', {
        'months': months,
        'sizes_over_time': sizes_over_time,
        'types': types,
        'sizes_by_type': sizes_by_type,
        'account_creation_date': request.user.date_joined,
    })