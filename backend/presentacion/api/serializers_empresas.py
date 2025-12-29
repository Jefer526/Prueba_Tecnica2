"""
Serializers para Empresas
"""
from rest_framework import serializers
from infraestructura.django_orm.models import EmpresaModel


class EmpresaListaSerializer(serializers.ModelSerializer):
    """Serializer para listar empresas"""
    class Meta:
        model = EmpresaModel
        fields = [
            'nit',
            'nombre',
            'direccion',
            'telefono',
            'activo',
            'fecha_creacion',
        ]


class EmpresaDetalleSerializer(serializers.ModelSerializer):
    """Serializer detallado de empresa"""
    class Meta:
        model = EmpresaModel
        fields = [
            'nit',
            'nombre',
            'direccion',
            'telefono',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
        ]


class EmpresaCrearSerializer(serializers.Serializer):
    """Serializer para crear empresas"""
    nit = serializers.CharField(max_length=20)
    nombre = serializers.CharField(max_length=200)
    direccion = serializers.CharField(required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)
