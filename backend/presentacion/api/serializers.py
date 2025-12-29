"""
Serializers - Capa de Presentación
DTOs para entrada y salida de la API REST
"""
from rest_framework import serializers
from dominio.entidades.producto import CategoriaProducto


# ==================== EMPRESA ====================

class EmpresaSerializer(serializers.Serializer):
    """Serializer para crear/actualizar empresas"""
    id = serializers.IntegerField(read_only=True)
    nombre = serializers.CharField(max_length=200)
    nit = serializers.CharField(max_length=20)
    direccion = serializers.CharField()
    telefono = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    activo = serializers.BooleanField(default=True)
    fecha_creacion = serializers.DateTimeField(read_only=True, required=False)
    fecha_actualizacion = serializers.DateTimeField(read_only=True, required=False)


class EmpresaListSerializer(serializers.Serializer):
    """Serializer para listar empresas (ligero)"""
    id = serializers.IntegerField()
    nombre = serializers.CharField()
    nit = serializers.CharField()
    email = serializers.EmailField()
    activo = serializers.BooleanField()


# ==================== PRODUCTO ====================

class ProductoCreateSerializer(serializers.Serializer):
    """Serializer para crear productos"""
    nombre = serializers.CharField(max_length=200)
    descripcion = serializers.CharField()
    precio_usd = serializers.DecimalField(max_digits=12, decimal_places=2)
    categoria = serializers.ChoiceField(choices=[
        ('TECNOLOGIA', 'Tecnología'),
        ('OFICINA', 'Oficina'),
        ('CONSUMIBLES', 'Consumibles'),
        ('EQUIPAMIENTO', 'Equipamiento'),
        ('OTROS', 'Otros'),
    ])
    empresa_id = serializers.IntegerField()
    stock_minimo = serializers.IntegerField(min_value=0)
    stock_maximo = serializers.IntegerField(min_value=1)
    stock_inicial = serializers.IntegerField(min_value=0)


class ProductoSerializer(serializers.Serializer):
    """Serializer completo para productos"""
    id = serializers.IntegerField(read_only=True)
    codigo = serializers.CharField(read_only=True)
    nombre = serializers.CharField()
    descripcion = serializers.CharField()
    precio_usd = serializers.DecimalField(max_digits=12, decimal_places=2)
    precio_cop = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    precio_eur = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    categoria = serializers.CharField()
    empresa_id = serializers.IntegerField()
    activo = serializers.BooleanField(default=True)
    fecha_creacion = serializers.DateTimeField(read_only=True, required=False)
    fecha_actualizacion = serializers.DateTimeField(read_only=True, required=False)


class ProductoListSerializer(serializers.Serializer):
    """Serializer para listar productos (ligero)"""
    id = serializers.IntegerField()
    codigo = serializers.CharField()
    nombre = serializers.CharField()
    precio_usd = serializers.DecimalField(max_digits=12, decimal_places=2)
    precio_cop = serializers.DecimalField(max_digits=12, decimal_places=2)
    precio_eur = serializers.DecimalField(max_digits=12, decimal_places=2)
    categoria = serializers.CharField()
    activo = serializers.BooleanField()


# ==================== INVENTARIO ====================

class InventarioSerializer(serializers.Serializer):
    """Serializer para inventario"""
    id = serializers.IntegerField(read_only=True)
    producto_id = serializers.IntegerField()
    empresa_id = serializers.IntegerField()
    stock_actual = serializers.IntegerField()
    stock_minimo = serializers.IntegerField()
    stock_maximo = serializers.IntegerField()
    requiere_reorden = serializers.BooleanField()
    estado_stock = serializers.CharField(read_only=True, required=False)
    ultima_actualizacion = serializers.DateTimeField(read_only=True, required=False)


# ==================== MOVIMIENTO ====================

class MovimientoCreateSerializer(serializers.Serializer):
    """Serializer para crear movimientos de inventario"""
    tipo_movimiento = serializers.ChoiceField(choices=[
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
        ('DEVOLUCION', 'Devolución'),
        ('TRANSFERENCIA', 'Transferencia'),
    ])
    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField(min_value=1)
    empresa_id = serializers.IntegerField()
    usuario_id = serializers.IntegerField()
    observaciones = serializers.CharField(required=False, allow_blank=True, default='')


class MovimientoSerializer(serializers.Serializer):
    """Serializer completo para movimientos"""
    id = serializers.IntegerField(read_only=True)
    tipo_movimiento = serializers.CharField()
    producto_id = serializers.IntegerField()
    cantidad = serializers.IntegerField()
    empresa_id = serializers.IntegerField()
    usuario_id = serializers.IntegerField()
    observaciones = serializers.CharField()
    fecha_movimiento = serializers.DateTimeField(read_only=True, required=False)


# ==================== RESPUESTAS ====================

class CrearProductoResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de creación de producto"""
    producto = ProductoSerializer()
    inventario = InventarioSerializer()
    mensaje = serializers.CharField()


class RegistrarMovimientoResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de registro de movimiento"""
    movimiento = MovimientoSerializer()
    inventario = InventarioSerializer()
    producto = ProductoSerializer()
    stock = serializers.DictField()
    alertas = serializers.ListField()
    mensaje = serializers.CharField()
