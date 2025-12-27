from django.contrib import admin
from .models import ConversacionIA, MensajeIA, AccionIA


@admin.register(ConversacionIA)
class ConversacionIAAdmin(admin.ModelAdmin):
    list_display = ['id', 'titulo', 'usuario', 'fecha_creacion', 'activo']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['titulo', 'usuario__correo']
    date_hierarchy = 'fecha_creacion'


@admin.register(MensajeIA)
class MensajeIAAdmin(admin.ModelAdmin):
    list_display = ['id', 'conversacion', 'rol', 'contenido_corto', 'fecha_creacion']
    list_filter = ['rol', 'fecha_creacion']
    search_fields = ['contenido']
    
    def contenido_corto(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_corto.short_description = 'Contenido'


@admin.register(AccionIA)
class AccionIAAdmin(admin.ModelAdmin):
    list_display = ['id', 'tipo_accion', 'exitoso', 'fecha_ejecucion']
    list_filter = ['tipo_accion', 'exitoso', 'fecha_ejecucion']
    date_hierarchy = 'fecha_ejecucion'