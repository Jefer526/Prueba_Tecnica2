"""
Serializers para Inventario - CAMPOS CORRECTOS
"""
from rest_framework import serializers
from infraestructura.django_orm.models import (
    InventarioModel,
    MovimientoInventarioModel,
    ProductoModel,
    EmpresaModel
)


class InventarioListaSerializer(serializers.ModelSerializer):
    """Serializer para listar inventarios"""
    producto_detalle = serializers.SerializerMethodField()
    empresa_detalle = serializers.SerializerMethodField()
    
    class Meta:
        model = InventarioModel
        fields = [
            'id',
            'producto',
            'empresa',
            'stock_actual',
            'stock_minimo',
            'stock_maximo',
            'requiere_reorden',
            'ultima_actualizacion',
            'producto_detalle',
            'empresa_detalle',
        ]
    
    def get_producto_detalle(self, obj):
        """Obtener detalles del producto"""
        try:
            return {
                'codigo': obj.producto.codigo,
                'nombre': obj.producto.nombre,
                'precio_usd': float(obj.producto.precio_usd),
                'categoria': obj.producto.categoria,
            }
        except Exception as e:
            print(f"Error producto_detalle: {e}")
            return None
    
    def get_empresa_detalle(self, obj):
        """Obtener detalles de la empresa"""
        try:
            return {
                'nit': obj.empresa.nit,
                'nombre': obj.empresa.nombre,
            }
        except Exception as e:
            print(f"Error empresa_detalle: {e}")
            return None


class InventarioDetalleSerializer(serializers.ModelSerializer):
    """Serializer detallado"""
    producto_detalle = serializers.SerializerMethodField()
    empresa_detalle = serializers.SerializerMethodField()
    
    class Meta:
        model = InventarioModel
        fields = '__all__'
    
    def get_fields(self):
        fields = super().get_fields()
        fields['producto_detalle'] = serializers.SerializerMethodField()
        fields['empresa_detalle'] = serializers.SerializerMethodField()
        return fields
    
    def get_producto_detalle(self, obj):
        try:
            return {
                'codigo': obj.producto.codigo,
                'nombre': obj.producto.nombre,
                'precio_usd': float(obj.producto.precio_usd),
            }
        except:
            return None
    
    def get_empresa_detalle(self, obj):
        try:
            return {
                'nit': obj.empresa.nit,
                'nombre': obj.empresa.nombre,
            }
        except:
            return None


class MovimientoInventarioListaSerializer(serializers.ModelSerializer):
    """Serializer para listar movimientos"""
    producto_detalle = serializers.SerializerMethodField()
    
    class Meta:
        model = MovimientoInventarioModel
        fields = [
            'id',
            'tipo_movimiento',
            'producto',
            'cantidad',
            'empresa',
            'usuario_id',
            'observaciones',
            'fecha_movimiento',
            'producto_detalle',
        ]
    
    def get_producto_detalle(self, obj):
        """Obtener detalles del producto"""
        try:
            return {
                'codigo': obj.producto.codigo,
                'nombre': obj.producto.nombre,
            }
        except:
            return None


class MovimientoInventarioCrearSerializer(serializers.Serializer):
    """Serializer para crear movimientos"""
    producto_id = serializers.IntegerField(required=True)
    tipo_movimiento = serializers.ChoiceField(
        choices=['ENTRADA', 'SALIDA', 'AJUSTE'],
        required=True
    )
    cantidad = serializers.IntegerField(required=True, min_value=1)
    observaciones = serializers.CharField(required=False, allow_blank=True)
    
    def validate_cantidad(self, value):
        if value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0")
        return value
