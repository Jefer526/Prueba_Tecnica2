from rest_framework import serializers
from .models import Empresa

class EmpresaSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Empresa"""
    
    total_productos = serializers.IntegerField(read_only=True)
    valor_total_inventario = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Empresa
        fields = [
            'nit',
            'nombre',
            'direccion',
            'telefono',
            'activo',
            'fecha_creacion',
            'fecha_actualizacion',
            'total_productos',
            'valor_total_inventario',
        ]
        read_only_fields = ['fecha_creacion', 'fecha_actualizacion']
    
    def validate_nit(self, valor):
        """Valida formato del NIT"""
        # Remover espacios y guiones
        nit_limpio = valor.replace(' ', '').replace('-', '')
        
        if not nit_limpio.isdigit():
            raise serializers.ValidationError(
                'El NIT debe contener solo números'
            )
        
        if len(nit_limpio) < 9 or len(nit_limpio) > 10:
            raise serializers.ValidationError(
                'El NIT debe tener entre 9 y 10 dígitos'
            )
        
        return valor
    
    def validate_telefono(self, valor):
        """Valida formato del teléfono"""
        # Remover espacios, guiones y paréntesis
        telefono_limpio = valor.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        if not telefono_limpio.isdigit():
            raise serializers.ValidationError(
                'El teléfono debe contener solo números'
            )
        
        if len(telefono_limpio) < 7 or len(telefono_limpio) > 15:
            raise serializers.ValidationError(
                'El teléfono debe tener entre 7 y 15 dígitos'
            )
        
        return valor


class EmpresaListaSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listar empresas"""
    
    total_productos = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Empresa
        fields = [
            'nit',
            'nombre',
            'telefono',
            'total_productos',
        ]