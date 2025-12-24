from rest_framework import serializers
from .models import TransaccionBlockchain, AuditoriaBlockchain

class TransaccionBlockchainSerializer(serializers.ModelSerializer):
    """Serializer para transacciones blockchain"""
    
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    esta_confirmada = serializers.BooleanField(read_only=True)
    tiempo_confirmacion = serializers.SerializerMethodField()
    
    class Meta:
        model = TransaccionBlockchain
        fields = [
            'id',
            'tipo_transaccion',
            'hash_transaccion',
            'bloque_numero',
            'datos_transaccion',
            'usuario',
            'usuario_nombre',
            'movimiento_inventario',
            'estado',
            'esta_confirmada',
            'gas_utilizado',
            'costo_transaccion',
            'fecha_creacion',
            'fecha_confirmacion',
            'tiempo_confirmacion',
            'direccion_remitente',
            'direccion_contrato',
        ]
        read_only_fields = [
            'id',
            'hash_transaccion',
            'bloque_numero',
            'estado',
            'gas_utilizado',
            'costo_transaccion',
            'fecha_creacion',
            'fecha_confirmacion',
        ]
    
    def get_tiempo_confirmacion(self, obj):
        """Calcula el tiempo de confirmación en segundos"""
        if obj.fecha_confirmacion and obj.fecha_creacion:
            diferencia = obj.fecha_confirmacion - obj.fecha_creacion
            return round(diferencia.total_seconds(), 2)
        return None


class AuditoriaBlockchainSerializer(serializers.ModelSerializer):
    """Serializer para auditorías blockchain"""
    
    transaccion_hash = serializers.CharField(
        source='transaccion.hash_transaccion',
        read_only=True
    )
    auditado_por_nombre = serializers.CharField(
        source='auditado_por.nombre_completo',
        read_only=True
    )
    
    class Meta:
        model = AuditoriaBlockchain
        fields = [
            'id',
            'transaccion',
            'transaccion_hash',
            'verificado',
            'datos_blockchain',
            'datos_base_datos',
            'coinciden',
            'discrepancias',
            'fecha_auditoria',
            'auditado_por',
            'auditado_por_nombre',
        ]
        read_only_fields = [
            'id',
            'fecha_auditoria',
        ]


class VerificarTransaccionSerializer(serializers.Serializer):
    """Serializer para verificar una transacción en blockchain"""
    
    hash_transaccion = serializers.CharField(max_length=66)
    
    def validate_hash_transaccion(self, valor):
        """Valida el formato del hash"""
        if not valor.startswith('0x'):
            raise serializers.ValidationError(
                'El hash debe comenzar con 0x'
            )
        if len(valor) != 66:
            raise serializers.ValidationError(
                'El hash debe tener 66 caracteres'
            )
        return valor