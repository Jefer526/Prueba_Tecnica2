"""
Configuración del Admin de Django
Permite gestionar datos desde el panel de administración
"""
from django.contrib import admin
from infraestructura.django_orm.models import (
    EmpresaModel,
    ProductoModel,
    InventarioModel,
    MovimientoInventarioModel,
    UsuarioModel
)


@admin.register(EmpresaModel)
class EmpresaAdmin(admin.ModelAdmin):
    """Admin para Empresa"""
    list_display = ['id', 'nombre', 'nit', 'email', 'activo', 'fecha_creacion']
    list_filter = ['activo', 'fecha_creacion']
    search_fields = ['nombre', 'nit', 'email']
    ordering = ['-fecha_creacion']


@admin.register(ProductoModel)
class ProductoAdmin(admin.ModelAdmin):
    """Admin para Producto"""
    list_display = ['id', 'codigo', 'nombre', 'categoria', 'precio_usd', 'empresa', 'activo']
    list_filter = ['categoria', 'activo', 'empresa']
    search_fields = ['codigo', 'nombre', 'descripcion']
    ordering = ['codigo']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']


@admin.register(InventarioModel)
class InventarioAdmin(admin.ModelAdmin):
    """Admin para Inventario"""
    list_display = ['id', 'producto', 'stock_actual', 'stock_minimo', 'stock_maximo', 'requiere_reorden', 'empresa']
    list_filter = ['requiere_reorden', 'empresa']
    search_fields = ['producto__codigo', 'producto__nombre']
    readonly_fields = ['ultima_actualizacion']
    
    def get_queryset(self, request):
        # Optimizar consultas
        qs = super().get_queryset(request)
        return qs.select_related('producto', 'empresa')


@admin.register(MovimientoInventarioModel)
class MovimientoAdmin(admin.ModelAdmin):
    """Admin para Movimiento de Inventario"""
    list_display = ['id', 'tipo_movimiento', 'producto', 'cantidad', 'empresa', 'usuario_id', 'fecha_movimiento']
    list_filter = ['tipo_movimiento', 'empresa', 'fecha_movimiento']
    search_fields = ['producto__codigo', 'producto__nombre', 'observaciones']
    ordering = ['-fecha_movimiento']
    readonly_fields = ['fecha_movimiento']
    
    def get_queryset(self, request):
        # Optimizar consultas
        qs = super().get_queryset(request)
        return qs.select_related('producto', 'empresa')


@admin.register(UsuarioModel)
class UsuarioAdmin(admin.ModelAdmin):
    """Admin para Usuario"""
    list_display = ['id', 'nombre', 'email', 'rol', 'activo', 'fecha_creacion']
    list_filter = ['rol', 'activo', 'fecha_creacion']
    search_fields = ['nombre', 'email']
    ordering = ['nombre']
    readonly_fields = ['password', 'fecha_creacion']  # No editar password directamente
