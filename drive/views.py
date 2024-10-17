from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from django.contrib import messages
from django.views.decorators.http import require_POST
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

@require_POST
def custom_logout(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('landing_page')