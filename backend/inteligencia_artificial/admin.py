from django.contrib import admin
from .models import PrediccionPrecio, ConsultaChatbot, AnalisisInventario

@admin.register(PrediccionPrecio)
class PrediccionPrecioAdmin(admin.ModelAdmin):
    """Configuración del admin para PrediccionPrecio"""
    
    list_display = [
        'producto',
        'precio_actual',
        'precio_predicho_30_dias',
        'tendencia',
        'confianza_prediccion',
        'fecha_prediccion'
    ]
    list_filter = ['tendencia', 'fecha_prediccion']
    search_fields = ['producto__nombre', 'producto__codigo']
    ordering = ['-fecha_prediccion']
    
    fieldsets = (
        ('Producto', {
            'fields': ('producto', 'precio_actual')
        }),
        ('Predicciones', {
            'fields': ('precio_predicho_30_dias', 'precio_predicho_60_dias', 'precio_predicho_90_dias')
        }),
        ('Análisis', {
            'fields': ('tendencia', 'confianza_prediccion', 'factores_considerados')
        }),
        ('Modelo', {
            'fields': ('modelo_utilizado', 'fecha_prediccion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_prediccion']


@admin.register(ConsultaChatbot)
class ConsultaChatbotAdmin(admin.ModelAdmin):
    """Configuración del admin para ConsultaChatbot"""
    
    list_display = [
        'usuario',
        'pregunta_resumida',
        'fecha_consulta',
        'tiempo_respuesta',
        'satisfaccion_usuario'
    ]
    list_filter = ['fecha_consulta', 'satisfaccion_usuario']
    search_fields = ['pregunta', 'respuesta', 'usuario__correo']
    ordering = ['-fecha_consulta']
    
    fieldsets = (
        ('Consulta', {
            'fields': ('usuario', 'pregunta', 'respuesta')
        }),
        ('Análisis', {
            'fields': ('contexto', 'tiempo_respuesta', 'satisfaccion_usuario')
        }),
        ('Fecha', {
            'fields': ('fecha_consulta',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['usuario', 'fecha_consulta', 'tiempo_respuesta']
    
    def pregunta_resumida(self, obj):
        """Muestra la pregunta resumida"""
        return obj.pregunta[:50] + '...' if len(obj.pregunta) > 50 else obj.pregunta
    pregunta_resumida.short_description = 'Pregunta'


@admin.register(AnalisisInventario)
class AnalisisInventarioAdmin(admin.ModelAdmin):
    """Configuración del admin para AnalisisInventario"""
    
    list_display = [
        'fecha_analisis',
        'productos_analizados',
        'total_recomendaciones',
        'ahorro_potencial'
    ]
    list_filter = ['fecha_analisis']
    ordering = ['-fecha_analisis']
    
    fieldsets = (
        ('Información General', {
            'fields': ('fecha_analisis', 'productos_analizados')
        }),
        ('Resultados', {
            'fields': ('recomendaciones', 'productos_bajo_stock', 'productos_sobrestock')
        }),
        ('Proyecciones', {
            'fields': ('proyeccion_demanda', 'ahorro_potencial')
        }),
    )
    
    readonly_fields = ['fecha_analisis']
    
    def total_recomendaciones(self, obj):
        """Muestra el total de recomendaciones"""
        return len(obj.recomendaciones)
    total_recomendaciones.short_description = 'Recomendaciones'