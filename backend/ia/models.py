from django.db import models
from django.conf import settings


class ConversacionIA(models.Model):
    """Modelo para guardar conversaciones del chatbot"""
    
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversaciones_ia'
    )
    titulo = models.CharField(max_length=200, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'ia_conversacion'
        ordering = ['-fecha_actualizacion']
        verbose_name = 'Conversación IA'
        verbose_name_plural = 'Conversaciones IA'
    
    def __str__(self):
        return f"{self.titulo or 'Conversación'} - {self.usuario.correo}"


class MensajeIA(models.Model):
    """Modelo para guardar mensajes individuales del chat"""
    
    ROLES = [
        ('user', 'Usuario'),
        ('assistant', 'Asistente'),
        ('system', 'Sistema'),
    ]
    
    conversacion = models.ForeignKey(
        ConversacionIA,
        on_delete=models.CASCADE,
        related_name='mensajes'
    )
    rol = models.CharField(max_length=20, choices=ROLES)
    contenido = models.TextField()
    metadatos = models.JSONField(default=dict, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ia_mensaje'
        ordering = ['fecha_creacion']
        verbose_name = 'Mensaje IA'
        verbose_name_plural = 'Mensajes IA'
    
    def __str__(self):
        return f"{self.get_rol_display()}: {self.contenido[:50]}..."


class AccionIA(models.Model):
    """Modelo para registrar acciones ejecutadas por el chatbot"""
    
    TIPOS_ACCION = [
        ('consulta_stock', 'Consulta de Stock'),
        ('generar_pdf', 'Generar PDF'),
        ('enviar_email', 'Enviar Email'),
        ('registrar_movimiento', 'Registrar Movimiento'),
        ('analisis', 'Análisis de Datos'),
    ]
    
    mensaje = models.ForeignKey(
        MensajeIA,
        on_delete=models.CASCADE,
        related_name='acciones'
    )
    tipo_accion = models.CharField(max_length=50, choices=TIPOS_ACCION)
    parametros = models.JSONField(default=dict)
    resultado = models.JSONField(default=dict)
    exitoso = models.BooleanField(default=True)
    fecha_ejecucion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ia_accion'
        ordering = ['-fecha_ejecucion']
        verbose_name = 'Acción IA'
        verbose_name_plural = 'Acciones IA'
    
    def __str__(self):
        return f"{self.get_tipo_accion_display()} - {self.fecha_ejecucion}"
