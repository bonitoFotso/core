from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class TimestampedModel(models.Model):
    """
    Modèle abstrait pour ajouter des champs de timestamp
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, TimestampedModel):
    """
    Modèle utilisateur personnalisé qui étend AbstractUser
    Vous pouvez ajouter des champs supplémentaires selon vos besoins
    """
    email = models.EmailField(
        _('email address'),
        unique=True,
        help_text=_('Required. Enter a valid email address.')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'auth_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f"{self.email}"

    @property
    def full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.username}".strip()

    def get_short_name(self):
        """Retourne le prénom de l'utilisateur"""
        return self.username
    

class Technicien(TimestampedModel):
    """
    Profil technicien lié à un utilisateur
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='technicien_profile'
    )
    nom = models.CharField(max_length=150, blank=True, null=True)
    prenom = models.CharField(max_length=150, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    experience = models.PositiveIntegerField(
        blank=True, 
        null=True, 
        help_text="Années d'expérience"
    )
    disponibilite = models.BooleanField(
        default=True, 
        help_text="Indique si le technicien est disponible"
    )
    photo = models.ImageField(
        upload_to='techniciens/photos/', 
        blank=True, 
        null=True
    )

    class Meta:
        verbose_name = 'Profil Technicien'
        verbose_name_plural = 'Profils Techniciens'

    def __str__(self):
        return f"Technicien: {self.nom} {self.prenom} ({self.user.email})"

    def save(self, *args, **kwargs):
        # Assurez-vous que l'utilisateur lié est marqué comme personnel
        if self.user:
            self.user.is_staff = True
            self.user.save()
        super().save(*args, **kwargs)
