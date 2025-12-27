from rest_framework import serializers
from .models import RegistroInventario, MovimientoInventario
from productos.models import Producto
from empresas.models import Empresa
from productos.serializers import ProductoListaSerializer
from empresas.serializers import EmpresaListaSerializer

class RegistroInventarioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo RegistroInventario"""
    
    producto_detalle = ProductoListaSerializer(source='producto', read_only=True)
    empresa_detalle = EmpresaListaSerializer(source='empresa', read_only=True)
    requiere_reorden = serializers.BooleanField(read_only=True)
    valor_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    # Usar SlugRelatedField para aceptar código y NIT
    producto = serializers.SlugRelatedField(
        slug_field='codigo',
        queryset=Producto.objects.all()
    )
    empresa = serializers.SlugRelatedField(
        slug_field='nit',
        queryset=Empresa.objects.all()
    )
    
    class Meta:
        model = RegistroInventario
        fields = [
            'id',
            'producto',
            'producto_detalle',
            'empresa',
            'empresa_detalle',
            'cantidad',
            'cantidad_minima',
            'ubicacion_bodega',
            'requiere_reorden',
            'valor_total',
            'fecha_ultima_entrada',
            'fecha_ultima_salida',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = [
            'id',
            'fecha_ultima_entrada',
            'fecha_ultima_salida',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
    
    def validate_cantidad(self, valor):
        """Valida que la cantidad sea no negativa"""
        if valor < 0:
            raise serializers.ValidationError(
                'La cantidad no puede ser negativa'
            )
        return valor
    
    def validate_cantidad_minima(self, valor):
        """Valida que la cantidad mínima sea positiva"""
        if valor < 0:
            raise serializers.ValidationError(
                'La cantidad mínima no puede ser negativa'
            )
        return valor


class MovimientoInventarioSerializer(serializers.ModelSerializer):
    """Serializer para el modelo MovimientoInventario"""
    
    usuario_nombre = serializers.SerializerMethodField()
    registro_inventario_detalle = RegistroInventarioSerializer(
        source='registro_inventario',
        read_only=True
    )
    
    class Meta:
        model = MovimientoInventario
        fields = [
            'id',
            'registro_inventario',
            'registro_inventario_detalle',
            'tipo_movimiento',
            'cantidad',
            'motivo',
            'usuario',
            'usuario_nombre',
            'fecha_movimiento',
            'hash_blockchain',
        ]
        read_only_fields = [
            'id',
            'usuario',
            'fecha_movimiento',
            'hash_blockchain',
        ]
    
    def get_usuario_nombre(self, obj):
        """Obtiene el nombre del usuario que realizó el movimiento"""
        if not obj.usuario:
            return 'Sistema'
        
        # Intentar obtener nombre_completo
        if hasattr(obj.usuario, 'nombre_completo') and obj.usuario.nombre_completo:
            return obj.usuario.nombre_completo
        
        # Si no tiene nombre_completo, usar correo
        if hasattr(obj.usuario, 'correo') and obj.usuario.correo:
            return obj.usuario.correo
        
        # Si no tiene correo, usar username
        if hasattr(obj.usuario, 'username') and obj.usuario.username:
            return obj.usuario.username
        
        # Último recurso
        return f'Usuario {obj.usuario.id}'
    
    def validate_cantidad(self, valor):
        """Valida que la cantidad sea positiva"""
        if valor <= 0:
            raise serializers.ValidationError(
                'La cantidad debe ser mayor a 0'
            )
        return valor
    
    def validate(self, datos):
        """Valida el movimiento según el tipo"""
        tipo_movimiento = datos.get('tipo_movimiento')
        cantidad = datos.get('cantidad')
        registro = datos.get('registro_inventario')
        
        # Si es salida, verificar que haya suficiente stock
        if tipo_movimiento == 'SALIDA' and registro:
            if cantidad > registro.cantidad:
                raise serializers.ValidationError({
                    'cantidad': f'No hay suficiente stock. Stock actual: {registro.cantidad}'
                })
        
        return datos


class InventarioPorEmpresaSerializer(serializers.Serializer):
    """Serializer para mostrar inventario agrupado por empresa"""
    
    empresa = EmpresaListaSerializer()
    registros = RegistroInventarioSerializer(many=True)
    total_productos = serializers.IntegerField()
    valor_total = serializers.DecimalField(max_digits=12, decimal_places=2)