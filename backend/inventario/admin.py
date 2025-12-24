from django.contrib import admin
from .models import RegistroInventario, MovimientoInventario

@admin.register(RegistroInventario)
class RegistroInventarioAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo RegistroInventario"""
    
    list_display = [
        'producto', 
        'empresa', 
        'cantidad', 
        'cantidad_minima', 
        'requiere_reorden', 
        'valor_total', 
        'ubicacion_bodega',
        'activo'
    ]
    list_filter = ['activo', 'empresa', 'fecha_creacion']
    search_fields = ['producto__nombre', 'producto__codigo', 'ubicacion_bodega']
    ordering = ['-fecha_actualizacion']
    
    fieldsets = (
        ('Producto y Empresa', {
            'fields': ('producto', 'empresa')
        }),
        ('Cantidades', {
            'fields': ('cantidad', 'cantidad_minima')
        }),
        ('Ubicación', {
            'fields': ('ubicacion_bodega',)
        }),
        ('Fechas de Movimiento', {
            'fields': ('fecha_ultima_entrada', 'fecha_ultima_salida'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('activo',)
        }),
        ('Información del Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'fecha_ultima_entrada', 
        'fecha_ultima_salida',
        'fecha_creacion', 
        'fecha_actualizacion'
    ]
    
    def requiere_reorden(self, obj):
        """Indica si requiere reorden"""
        return obj.requiere_reorden
    requiere_reorden.boolean = True
    requiere_reorden.short_description = 'Requiere Reorden'
    
    def valor_total(self, obj):
        """Muestra el valor total"""
        return f"${obj.valor_total:,.2f}"
    valor_total.short_description = 'Valor Total'


@admin.register(MovimientoInventario)
class MovimientoInventarioAdmin(admin.ModelAdmin):
    """Configuración del admin para el modelo MovimientoInventario"""
    
    list_display = [
        'registro_inventario',
        'tipo_movimiento',
        'cantidad',
        'usuario',
        'fecha_movimiento',
        'tiene_blockchain'
    ]
    list_filter = ['tipo_movimiento', 'fecha_movimiento']
    search_fields = ['motivo', 'registro_inventario__producto__nombre']
    ordering = ['-fecha_movimiento']
    
    fieldsets = (
        ('Movimiento', {
            'fields': ('registro_inventario', 'tipo_movimiento', 'cantidad', 'motivo')
        }),
        ('Usuario y Fecha', {
            'fields': ('usuario', 'fecha_movimiento')
        }),
        ('Blockchain', {
            'fields': ('hash_blockchain',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['usuario', 'fecha_movimiento', 'hash_blockchain']
    
    def tiene_blockchain(self, obj):
        """Indica si tiene registro en blockchain"""
        return bool(obj.hash_blockchain)
    tiene_blockchain.boolean = True
    tiene_blockchain.short_description = 'En Blockchain'