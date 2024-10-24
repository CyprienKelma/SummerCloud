from django.db import models
import os
from django.contrib.auth.models import User

def user_directory_path(instance, filename):
    """
    Fonction qui génère le chemin du fichier selon qu'il y ait, ou non, des sous-dossiers.
    Le chemin pourrait être par ex : media/user_<user_id>/dossier1/dossier2/filename
    """
    # On part du chemin de base : le repertoire racine
    path = f'user_{instance.owner.id}'

    # Mais si le fichier est dans un sous-dossier, alors on ajoute au chemin
    if instance.folder:
        path = os.path.join(path, instance.folder.get_full_path())

    return os.path.join(path, filename)


class File(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)  # le user qui possède ce fichier
    name = models.CharField(max_length=255) # nom du file
    file = models.FileField(upload_to=user_directory_path) # Chemin de ce fichier dans le dossier 'media'
    size = models.BigIntegerField()  # en octets
    upload_date = models.DateTimeField(auto_now_add=True)  # Date d'ajout du fichier sur SummerDrive
    folder = models.ForeignKey('Folder', on_delete=models.CASCADE, null=True, blank=True)  # Dossier parent

    def __str__(self):
        return self.name

    # Pour afficher la des fichiers en mb
    @property
    def size_in_mb(self):
        return round(self.size / (1024 * 1024), 2)


class Folder(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    parent_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_full_path(self):
        """
        Return le chemin complet du dossier (-> y compris les dossiers parents)
        Par ex : dossier_racine_de_l'user/mon_dossier_1/un_autre_dossier_2
        """
        if self.parent_folder:
            return os.path.join(self.parent_folder.get_full_path(), self.name)
        return self.name