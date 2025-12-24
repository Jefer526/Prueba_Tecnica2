from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Configuración del admin para el modelo Usuario"""
    
    list_display = ['correo', 'nombre_completo', 'tipo_usuario', 'es_administrador', 'esta_activo', 'fecha_creacion']
    list_filter = ['tipo_usuario', 'es_administrador', 'esta_activo', 'fecha_creacion']
    search_fields = ['correo', 'nombre_completo']
    ordering = ['-fecha_creacion']
    
    fieldsets = (
        ('Información de Acceso', {
            'fields': ('correo', 'password')
        }),
        ('Información Personal', {
            'fields': ('nombre_completo',)
        }),
        ('Permisos y Tipo', {
            'fields': ('tipo_usuario', 'es_administrador', 'esta_activo', 'is_staff', 'is_superuser')
        }),
        ('Fechas Importantes', {
            'fields': ('fecha_creacion', 'fecha_actualizacion')
        }),
    )
    
    add_fieldsets = (
        ('Crear Nuevo Usuario', {
            'classes': ('wide',),
            'fields': ('correo', 'nombre_completo', 'tipo_usuario', 'password1', 'password2', 'es_administrador'),
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    filter_horizontal = ()