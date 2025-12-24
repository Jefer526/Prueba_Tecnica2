from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo Producto"""
    
    list_display = ['codigo', 'nombre', 'empresa', 'precio_usd', 'precio_cop', 'precio_eur', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'empresa', 'fecha_creacion']
    search_fields = ['codigo', 'nombre', 'caracteristicas']
    ordering = ['nombre']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'caracteristicas', 'empresa')
        }),
        ('Precios', {
            'fields': ('precio_usd', 'precio_cop', 'precio_eur')
        }),
        ('Imagen', {
            'fields': ('imagen',)
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
    
    def save_model(self, request, obj, form, change):
        """Calcula precios antes de guardar"""
        obj.calcular_precios_monedas()
        super().save_model(request, obj, form, change)