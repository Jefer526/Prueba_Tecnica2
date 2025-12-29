"""
Serializers para Productos
"""
from rest_framework import serializers
from infraestructura.django_orm.models import ProductoModel, EmpresaModel


class EmpresaSimpleSerializer(serializers.ModelSerializer):
    """Serializer simple de Empresa"""
    class Meta:
        model = EmpresaModel
        fields = ['nit', 'nombre']


class ProductoListaSerializer(serializers.ModelSerializer):
    """Serializer para listar productos"""
    empresa_detalle = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductoModel
        fields = [
            'id',
            'codigo',
            'nombre',
            'descripcion',
            'precio_usd',
            'precio_cop',
            'precio_eur',
            'categoria',
            'empresa',
            'empresa_detalle',
            'activo',
            'fecha_creacion',
        ]
    
    def get_empresa_detalle(self, obj):
        """Obtener detalles de la empresa"""
        try:
            return {
                'nit': obj.empresa.nit,
                'nombre': obj.empresa.nombre,
            }
        except:
            return None


class ProductoDetalleSerializer(serializers.ModelSerializer):
    """Serializer detallado de producto"""
    empresa_detalle = EmpresaSimpleSerializer(source='empresa', read_only=True)
    
    class Meta:
        model = ProductoModel
        fields = [
            'id',
            'codigo',
            'nombre',
            'descripcion',
            'precio_usd',
            'precio_cop',
            'precio_eur',
            'categoria',
            'empresa',
            'empresa_detalle',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]


class ProductoCrearSerializer(serializers.Serializer):
    """Serializer para crear productos"""
    nombre = serializers.CharField(max_length=200)
    descripcion = serializers.CharField(required=False, allow_blank=True)
    precio_usd = serializers.DecimalField(max_digits=10, decimal_places=2)
    categoria = serializers.ChoiceField(choices=[
        'TECNOLOGIA', 'ROPA', 'ALIMENTOS', 'HOGAR', 'DEPORTES', 'OTROS'
    ])
    empresa_nit = serializers.CharField(max_length=20)
