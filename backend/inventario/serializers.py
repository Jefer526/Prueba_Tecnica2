from rest_framework import serializers
from .models import RegistroInventario, MovimientoInventario
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
    
    def validate(self, datos):
        """Valida que no exista un registro duplicado"""
        producto = datos.get('producto')
        empresa = datos.get('empresa')
        
        # Verificar que el producto pertenezca a la empresa
        if producto and empresa:
            if producto.empresa != empresa:
                raise serializers.ValidationError({
                    'producto': 'El producto no pertenece a la empresa seleccionada'
                })
        
        return datos
    
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
    
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
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