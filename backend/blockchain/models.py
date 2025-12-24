from django.db import models
from autenticacion.models import Usuario
from inventario.models import MovimientoInventario

class TransaccionBlockchain(models.Model):
    """Modelo para registrar transacciones en blockchain"""
    
    TIPO_TRANSACCION_CHOICES = [
        ('REGISTRO_PRODUCTO', 'Registro de Producto'),
        ('MOVIMIENTO_INVENTARIO', 'Movimiento de Inventario'),
        ('ACTUALIZACION_PRECIO', 'Actualización de Precio'),
        ('TRANSFERENCIA_EMPRESA', 'Transferencia entre Empresas'),
    ]
    
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('FALLIDA', 'Fallida'),
    ]
    
    tipo_transaccion = models.CharField(
        max_length=50,
        choices=TIPO_TRANSACCION_CHOICES,
        verbose_name='Tipo de Transacción'
    )
    hash_transaccion = models.CharField(
        max_length=66,
        unique=True,
        verbose_name='Hash de Transacción',
        help_text='Hash único de la transacción en blockchain'
    )
    bloque_numero = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='Número de Bloque'
    )
    datos_transaccion = models.JSONField(
        verbose_name='Datos de la Transacción',
        help_text='Información almacenada en la transacción'
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='transacciones_blockchain',
        verbose_name='Usuario'
    )
    movimiento_inventario = models.ForeignKey(
        MovimientoInventario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transacciones_blockchain',
        verbose_name='Movimiento de Inventario'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='PENDIENTE',
        verbose_name='Estado'
    )
    gas_utilizado = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name='Gas Utilizado'
    )
    costo_transaccion = models.DecimalField(
        max_digits=18,
        decimal_places=8,
        null=True,
        blank=True,
        verbose_name='Costo de Transacción (ETH)'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_confirmacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Confirmación'
    )
    direccion_remitente = models.CharField(
        max_length=42,
        verbose_name='Dirección Remitente',
        blank=True
    )
    direccion_contrato = models.CharField(
        max_length=42,
        verbose_name='Dirección del Contrato',
        blank=True
    )
    
    class Meta:
        verbose_name = 'Transacción Blockchain'
        verbose_name_plural = 'Transacciones Blockchain'
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['hash_transaccion']),
            models.Index(fields=['estado']),
        ]
    
    def __str__(self):
        return f"{self.tipo_transaccion} - {self.hash_transaccion[:10]}..."
    
    @property
    def esta_confirmada(self):
        """Verifica si la transacción está confirmada"""
        return self.estado == 'CONFIRMADA'


class AuditoriaBlockchain(models.Model):
    """Modelo para auditoría y verificación de datos en blockchain"""
    
    transaccion = models.ForeignKey(
        TransaccionBlockchain,
        on_delete=models.CASCADE,
        related_name='auditorias',
        verbose_name='Transacción'
    )
    verificado = models.BooleanField(
        default=False,
        verbose_name='Verificado'
    )
    datos_blockchain = models.JSONField(
        verbose_name='Datos desde Blockchain',
        help_text='Datos recuperados directamente de la blockchain'
    )
    datos_base_datos = models.JSONField(
        verbose_name='Datos desde Base de Datos',
        help_text='Datos almacenados en la base de datos local'
    )
    coinciden = models.BooleanField(
        default=True,
        verbose_name='Datos Coinciden'
    )
    discrepancias = models.JSONField(
        verbose_name='Discrepancias',
        default=list,
        help_text='Lista de discrepancias encontradas'
    )
    fecha_auditoria = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Auditoría'
    )
    auditado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Auditado Por'
    )
    
    class Meta:
        verbose_name = 'Auditoría Blockchain'
        verbose_name_plural = 'Auditorías Blockchain'
        ordering = ['-fecha_auditoria']
    
    def __str__(self):
        estado = "✓ Verificado" if self.verificado else "✗ No verificado"
        return f"Auditoría {self.transaccion.hash_transaccion[:10]}... - {estado}"