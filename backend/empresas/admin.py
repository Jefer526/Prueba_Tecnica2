from django.contrib import admin
from .models import Empresa

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Empresa"""
    
    list_display = ['nit', 'nombre', 'telefono', 'activo', 'total_productos', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nit', 'nombre', 'telefono']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nit', 'nombre')
        }),
        ('Información de Contacto', {
            'fields': ('direccion', 'telefono')
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def total_productos(self, obj):
        """Muestra el total de productos"""
        return obj.total_productos()
    total_productos.short_description = 'Total Productos'