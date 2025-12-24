from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from decimal import Decimal
import hashlib
import json
import random
from .models import TransaccionBlockchain, AuditoriaBlockchain
from .serializers import (
    TransaccionBlockchainSerializer,
    AuditoriaBlockchainSerializer,
    VerificarTransaccionSerializer
)
from inventario.models import MovimientoInventario

class TransaccionBlockchainViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para transacciones blockchain"""
    
    queryset = TransaccionBlockchain.objects.all()
    serializer_class = TransaccionBlockchainSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtra transacciones según el usuario"""
        if self.request.user.tiene_permiso_administrador():
            return TransaccionBlockchain.objects.all()
        return TransaccionBlockchain.objects.filter(usuario=self.request.user)
    
    @action(detail=False, methods=['post'])
    def registrar_movimiento(self, request):
        """Registra un movimiento de inventario en blockchain"""
        movimiento_id = request.data.get('movimiento_id')
        
        if not movimiento_id:
            return Response({
                'error': 'Debe proporcionar el ID del movimiento'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            movimiento = MovimientoInventario.objects.get(id=movimiento_id)
        except MovimientoInventario.DoesNotExist:
            return Response({
                'error': 'Movimiento no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar si ya está registrado
        if TransaccionBlockchain.objects.filter(movimiento_inventario=movimiento).exists():
            return Response({
                'error': 'Este movimiento ya está registrado en blockchain'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Preparar datos de la transacción
        datos_transaccion = {
            'movimiento_id': movimiento.id,
            'tipo_movimiento': movimiento.tipo_movimiento,
            'producto': {
                'codigo': movimiento.registro_inventario.producto.codigo,
                'nombre': movimiento.registro_inventario.producto.nombre,
            },
            'empresa': {
                'nit': movimiento.registro_inventario.empresa.nit,
                'nombre': movimiento.registro_inventario.empresa.nombre,
            },
            'cantidad': movimiento.cantidad,
            'fecha': movimiento.fecha_movimiento.isoformat(),
            'usuario': movimiento.usuario.correo if movimiento.usuario else 'Sistema',
            'timestamp': timezone.now().isoformat()
        }
        
        # Generar hash de la transacción (simulado)
        hash_transaccion = self._generar_hash_transaccion(datos_transaccion)
        
        # Simular registro en blockchain
        bloque_numero = random.randint(1000000, 9999999)
        gas_utilizado = random.randint(21000, 50000)
        costo_transaccion = Decimal(gas_utilizado * 0.000000020)  # Simulación de costo en ETH
        
        # Crear transacción
        transaccion = TransaccionBlockchain.objects.create(
            tipo_transaccion='MOVIMIENTO_INVENTARIO',
            hash_transaccion=hash_transaccion,
            bloque_numero=bloque_numero,
            datos_transaccion=datos_transaccion,
            usuario=request.user,
            movimiento_inventario=movimiento,
            estado='CONFIRMADA',
            gas_utilizado=gas_utilizado,
            costo_transaccion=costo_transaccion.quantize(Decimal('0.00000001')),
            fecha_confirmacion=timezone.now(),
            direccion_remitente='0x' + hashlib.sha256(request.user.correo.encode()).hexdigest()[:40],
            direccion_contrato='0xABCDEF1234567890ABCDEF1234567890ABCDEF12'  # Simulado
        )
        
        # Actualizar hash en movimiento
        movimiento.hash_blockchain = hash_transaccion
        movimiento.save()
        
        serializer = TransaccionBlockchainSerializer(transaccion)
        
        return Response({
            'mensaje': 'Transacción registrada exitosamente en blockchain',
            'transaccion': serializer.data,
            'explorer_url': f'https://etherscan.io/tx/{hash_transaccion}'  # Simulado
        })
    
    def _generar_hash_transaccion(self, datos):
        """Genera un hash único para la transacción"""
        datos_string = json.dumps(datos, sort_keys=True)
        hash_objeto = hashlib.sha256(datos_string.encode())
        return '0x' + hash_objeto.hexdigest()
    
    @action(detail=True, methods=['get'])
    def detalles_blockchain(self, request, pk=None):
        """Obtiene detalles completos de la transacción en blockchain"""
        transaccion = self.get_object()
        
        # Simular consulta a blockchain real
        detalles_blockchain = {
            'hash': transaccion.hash_transaccion,
            'bloque': transaccion.bloque_numero,
            'confirmaciones': random.randint(10, 100),
            'timestamp': transaccion.fecha_confirmacion.isoformat() if transaccion.fecha_confirmacion else None,
            'from': transaccion.direccion_remitente,
            'to': transaccion.direccion_contrato,
            'gas_usado': transaccion.gas_utilizado,
            'gas_price': '20 Gwei',
            'costo_transaccion': str(transaccion.costo_transaccion),
            'estado': transaccion.estado,
            'datos': transaccion.datos_transaccion
        }
        
        return Response(detalles_blockchain)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Obtiene estadísticas de transacciones blockchain"""
        total_transacciones = TransaccionBlockchain.objects.count()
        confirmadas = TransaccionBlockchain.objects.filter(estado='CONFIRMADA').count()
        pendientes = TransaccionBlockchain.objects.filter(estado='PENDIENTE').count()
        
        costo_total = TransaccionBlockchain.objects.filter(
            costo_transaccion__isnull=False
        ).aggregate(total=sum('costo_transaccion'))['total'] or 0
        
        return Response({
            'total_transacciones': total_transacciones,
            'confirmadas': confirmadas,
            'pendientes': pendientes,
            'tasa_exito': round((confirmadas / total_transacciones * 100), 2) if total_transacciones > 0 else 0,
            'costo_total_eth': str(costo_total),
            'ultima_transaccion': TransaccionBlockchainSerializer(
                TransaccionBlockchain.objects.order_by('-fecha_creacion').first()
            ).data if total_transacciones > 0 else None
        })


class AuditoriaBlockchainViewSet(viewsets.ModelViewSet):
    """ViewSet para auditorías blockchain"""
    
    queryset = AuditoriaBlockchain.objects.all()
    serializer_class = AuditoriaBlockchainSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def auditar_transaccion(self, request):
        """Realiza una auditoría de una transacción comparando blockchain con BD"""
        hash_transaccion = request.data.get('hash_transaccion')
        
        if not hash_transaccion:
            return Response({
                'error': 'Debe proporcionar el hash de la transacción'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            transaccion = TransaccionBlockchain.objects.get(hash_transaccion=hash_transaccion)
        except TransaccionBlockchain.DoesNotExist:
            return Response({
                'error': 'Transacción no encontrada'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Simular obtención de datos desde blockchain
        datos_blockchain = transaccion.datos_transaccion.copy()
        datos_blockchain['verificado_en_blockchain'] = True
        datos_blockchain['timestamp_verificacion'] = timezone.now().isoformat()
        
        # Datos de la base de datos local
        datos_bd = transaccion.datos_transaccion.copy()
        
        # Comparar datos
        discrepancias = []
        coinciden = True
        
        # En un escenario real, aquí compararíamos campo por campo
        # Para la demo, simularemos que coinciden en el 95% de los casos
        if random.random() > 0.95:
            coinciden = False
            discrepancias.append({
                'campo': 'cantidad',
                'valor_blockchain': datos_blockchain.get('cantidad'),
                'valor_bd': datos_bd.get('cantidad'),
                'descripcion': 'Diferencia detectada en la cantidad'
            })
        
        # Crear auditoría
        auditoria = AuditoriaBlockchain.objects.create(
            transaccion=transaccion,
            verificado=True,
            datos_blockchain=datos_blockchain,
            datos_base_datos=datos_bd,
            coinciden=coinciden,
            discrepancias=discrepancias,
            auditado_por=request.user
        )
        
        serializer = AuditoriaBlockchainSerializer(auditoria)
        
        return Response({
            'mensaje': 'Auditoría completada exitosamente',
            'resultado': 'EXITOSA' if coinciden else 'CON DISCREPANCIAS',
            'auditoria': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def auditar_todas(self, request):
        """Audita todas las transacciones pendientes de verificación"""
        transacciones = TransaccionBlockchain.objects.filter(
            estado='CONFIRMADA'
        ).exclude(
            auditorias__verificado=True
        )[:10]  # Limitar a 10 para demo
        
        auditorias_creadas = []
        
        for transaccion in transacciones:
            # Simular auditoría
            datos_blockchain = transaccion.datos_transaccion.copy()
            datos_blockchain['verificado_en_blockchain'] = True
            
            auditoria = AuditoriaBlockchain.objects.create(
                transaccion=transaccion,
                verificado=True,
                datos_blockchain=datos_blockchain,
                datos_base_datos=transaccion.datos_transaccion,
                coinciden=True,
                discrepancias=[],
                auditado_por=request.user
            )
            
            auditorias_creadas.append(auditoria)
        
        return Response({
            'mensaje': f'Se auditaron {len(auditorias_creadas)} transacciones',
            'auditorias': AuditoriaBlockchainSerializer(auditorias_creadas, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def reporte_integridad(self, request):
        """Genera un reporte de integridad del sistema"""
        total_transacciones = TransaccionBlockchain.objects.count()
        total_auditadas = AuditoriaBlockchain.objects.filter(verificado=True).count()
        con_discrepancias = AuditoriaBlockchain.objects.filter(coinciden=False).count()
        
        integridad_porcentaje = 100
        if total_auditadas > 0:
            integridad_porcentaje = round(
                ((total_auditadas - con_discrepancias) / total_auditadas) * 100,
                2
            )
        
        return Response({
            'total_transacciones': total_transacciones,
            'total_auditadas': total_auditadas,
            'con_discrepancias': con_discrepancias,
            'integridad_porcentaje': integridad_porcentaje,
            'estado': 'EXCELENTE' if integridad_porcentaje >= 95 else 'ACEPTABLE' if integridad_porcentaje >= 80 else 'REQUIERE ATENCION',
            'ultima_auditoria': AuditoriaBlockchainSerializer(
                AuditoriaBlockchain.objects.order_by('-fecha_auditoria').first()
            ).data if total_auditadas > 0 else None
        })