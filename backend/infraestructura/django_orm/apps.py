"""
Configuración de la app de infraestructura para Django
"""
from django.apps import AppConfig


class InfraestructuraConfig(AppConfig):
    """Configuración de la aplicación de infraestructura"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'infraestructura.django_orm'
    verbose_name = 'Infraestructura - Persistencia'
