from rest_framework import serializers
from .models import Producto
from empresas.serializers import EmpresaListaSerializer

class ProductoSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Producto"""
    
    empresa_detalle = EmpresaListaSerializer(source='empresa', read_only=True)
    imagen_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'codigo',
            'nombre',
            'caracteristicas',
            'precio_usd',
            'precio_cop',
            'precio_eur',
            'empresa',
            'empresa_detalle',
            'imagen',
            'imagen_url',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']
    
    def get_imagen_url(self, obj):
        """Obtiene la URL completa de la imagen"""
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
        return None
    
    def validate_precio_usd(self, valor):
        """Valida que el precio sea positivo"""
        if valor <= 0:
            raise serializers.ValidationError(
                'El precio debe ser mayor a 0'
            )
        return valor
    
    def validate_codigo(self, valor):
        """Valida que el código sea único"""
        codigo_upper = valor.upper()
        
        # Si es actualización, excluir el producto actual
        instance = getattr(self, 'instance', None)
        queryset = Producto.objects.filter(codigo=codigo_upper)
        
        if instance:
            queryset = queryset.exclude(pk=instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                'Ya existe un producto con este código'
            )
        
        return codigo_upper


class ProductoCrearSerializer(serializers.ModelSerializer):
    """Serializer para crear productos (sin campos calculados)"""
    
    class Meta:
        model = Producto
        fields = [
            'codigo',
            'nombre',
            'caracteristicas',
            'precio_usd',
            'precio_cop',
            'precio_eur',
            'empresa',
            'imagen',
        ]
    
    def validate_precio_usd(self, valor):
        """Valida que el precio sea positivo"""
        if valor <= 0:
            raise serializers.ValidationError(
                'El precio debe ser mayor a 0'
            )
        return valor


class ProductoListaSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar productos"""
    
    empresa_nombre = serializers.CharField(source='empresa.nombre', read_only=True)
    
    class Meta:
        model = Producto
        fields = [
            'id',
            'codigo',
            'nombre',
            'precio_usd',
            'empresa',
            'empresa_nombre',
            'activo',
        ]