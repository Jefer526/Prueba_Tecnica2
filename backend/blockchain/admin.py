from django.contrib import admin
from .models import TransaccionBlockchain, AuditoriaBlockchain

@admin.register(TransaccionBlockchain)
class TransaccionBlockchainAdmin(admin.ModelAdmin):
    """Configuración del admin para TransaccionBlockchain"""
    
    list_display = [
        'hash_resumido',
        'tipo_transaccion',
        'estado',
        'bloque_numero',
        'usuario',
        'costo_transaccion',
        'fecha_creacion'
    ]
    list_filter = ['tipo_transaccion', 'estado', 'fecha_creacion']
    search_fields = ['hash_transaccion', 'usuario__correo']
    ordering = ['-fecha_creacion']
    
    fieldsets = (
        ('Transacción', {
            'fields': ('tipo_transaccion', 'hash_transaccion', 'estado')
        }),
        ('Blockchain', {
            'fields': ('bloque_numero', 'direccion_remitente', 'direccion_contrato')
        }),
        ('Datos', {
            'fields': ('datos_transaccion', 'movimiento_inventario')
        }),
        ('Costos', {
            'fields': ('gas_utilizado', 'costo_transaccion')
        }),
        ('Usuario y Fechas', {
            'fields': ('usuario', 'fecha_creacion', 'fecha_confirmacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'hash_transaccion',
        'bloque_numero',
        'estado',
        'gas_utilizado',
        'costo_transaccion',
        'fecha_creacion',
        'fecha_confirmacion'
    ]
    
    def hash_resumido(self, obj):
        """Muestra el hash resumido"""
        return f"{obj.hash_transaccion[:10]}...{obj.hash_transaccion[-8:]}"
    hash_resumido.short_description = 'Hash'


@admin.register(AuditoriaBlockchain)
class AuditoriaBlockchainAdmin(admin.ModelAdmin):
    """Configuración del admin para AuditoriaBlockchain"""
    
    list_display = [
        'transaccion',
        'verificado',
        'coinciden',
        'total_discrepancias',
        'fecha_auditoria',
        'auditado_por'
    ]
    list_filter = ['verificado', 'coinciden', 'fecha_auditoria']
    search_fields = ['transaccion__hash_transaccion', 'auditado_por__correo']
    ordering = ['-fecha_auditoria']
    
    fieldsets = (
        ('Auditoría', {
            'fields': ('transaccion', 'verificado', 'coinciden')
        }),
        ('Datos Comparados', {
            'fields': ('datos_blockchain', 'datos_base_datos')
        }),
        ('Discrepancias', {
            'fields': ('discrepancias',)
        }),
        ('Información', {
            'fields': ('auditado_por', 'fecha_auditoria'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_auditoria']
    
    def total_discrepancias(self, obj):
        """Muestra el total de discrepancias"""
        return len(obj.discrepancias)
    total_discrepancias.short_description = 'Discrepancias'