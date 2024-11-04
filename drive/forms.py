from django import forms
from .models import File
from .models import Folder


# Formulaire pour l'upload d'un fichier par le user
class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file', 'folder']

    def clean_file(self):
        file = self.cleaned_data['file']
        # On limite la taille des fichiers à 40 MB
        if file.size > 40 * 1024 * 1024: # (1024)^2 car on stock la taille en octets
            raise forms.ValidationError("ERREUR : Taille du fichier superieur à 40MB.")
        return file


# Formulaire pour la création d'un nouveau dossier
class FolderCreateForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent_folder']

    def clean_name(self):
        name = self.cleaned_data['name']
        # Limite de la taille par soucis d'affichage
        if not name or len(name) > 255:
            raise forms.ValidationError("ERREUR : Nom du dossier est invalide ou trop long.")
        return name
