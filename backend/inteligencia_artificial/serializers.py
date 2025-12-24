from rest_framework import serializers
from .models import PrediccionPrecio, ConsultaChatbot, AnalisisInventario
from productos.serializers import ProductoListaSerializer

class PrediccionPrecioSerializer(serializers.ModelSerializer):
    """Serializer para predicciones de precio"""
    
    producto_detalle = ProductoListaSerializer(source='producto', read_only=True)
    variacion_30_dias = serializers.SerializerMethodField()
    variacion_60_dias = serializers.SerializerMethodField()
    variacion_90_dias = serializers.SerializerMethodField()
    
    class Meta:
        model = PrediccionPrecio
        fields = [
            'id',
            'producto',
            'producto_detalle',
            'precio_actual',
            'precio_predicho_30_dias',
            'precio_predicho_60_dias',
            'precio_predicho_90_dias',
            'variacion_30_dias',
            'variacion_60_dias',
            'variacion_90_dias',
            'tendencia',
            'confianza_prediccion',
            'factores_considerados',
            'fecha_prediccion',
            'modelo_utilizado',
        ]
        read_only_fields = ['id', 'fecha_prediccion']
    
    def get_variacion_30_dias(self, obj):
        """Calcula la variación porcentual a 30 días"""
        if obj.precio_predicho_30_dias and obj.precio_actual:
            variacion = ((obj.precio_predicho_30_dias - obj.precio_actual) / obj.precio_actual) * 100
            return round(float(variacion), 2)
        return None
    
    def get_variacion_60_dias(self, obj):
        """Calcula la variación porcentual a 60 días"""
        if obj.precio_predicho_60_dias and obj.precio_actual:
            variacion = ((obj.precio_predicho_60_dias - obj.precio_actual) / obj.precio_actual) * 100
            return round(float(variacion), 2)
        return None
    
    def get_variacion_90_dias(self, obj):
        """Calcula la variación porcentual a 90 días"""
        if obj.precio_predicho_90_dias and obj.precio_actual:
            variacion = ((obj.precio_predicho_90_dias - obj.precio_actual) / obj.precio_actual) * 100
            return round(float(variacion), 2)
        return None


class ConsultaChatbotSerializer(serializers.ModelSerializer):
    """Serializer para consultas al chatbot"""
    
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    
    class Meta:
        model = ConsultaChatbot
        fields = [
            'id',
            'usuario',
            'usuario_nombre',
            'pregunta',
            'respuesta',
            'contexto',
            'fecha_consulta',
            'tiempo_respuesta',
            'satisfaccion_usuario',
        ]
        read_only_fields = [
            'id',
            'usuario',
            'respuesta',
            'contexto',
            'fecha_consulta',
            'tiempo_respuesta',
        ]


class CrearConsultaChatbotSerializer(serializers.Serializer):
    """Serializer para crear consultas al chatbot"""
    
    pregunta = serializers.CharField(max_length=1000)


class AnalisisInventarioSerializer(serializers.ModelSerializer):
    """Serializer para análisis de inventario"""
    
    class Meta:
        model = AnalisisInventario
        fields = [
            'id',
            'fecha_analisis',
            'productos_analizados',
            'recomendaciones',
            'productos_bajo_stock',
            'productos_sobrestock',
            'proyeccion_demanda',
            'ahorro_potencial',
        ]
        read_only_fields = ['id', 'fecha_analisis']