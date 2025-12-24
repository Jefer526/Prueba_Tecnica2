from django.db import models
from empresas.models import Empresa
from productos.models import Producto
from autenticacion.models import Usuario

class RegistroInventario(models.Model):
    """Modelo para gestionar el inventario de productos por empresa"""
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='registros_inventario',
        verbose_name='Producto'
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='registros_inventario',
        verbose_name='Empresa'
    )
    cantidad = models.IntegerField(
        default=0,
        verbose_name='Cantidad en Stock'
    )
    cantidad_minima = models.IntegerField(
        default=10,
        verbose_name='Cantidad Mínima',
        help_text='Nivel mínimo de stock antes de reordenar'
    )
    ubicacion_bodega = models.CharField(
        max_length=100,
        verbose_name='Ubicación en Bodega',
        blank=True
    )
    fecha_ultima_entrada = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha Última Entrada'
    )
    fecha_ultima_salida = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha Última Salida'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        verbose_name = 'Registro de Inventario'
        verbose_name_plural = 'Registros de Inventario'
        unique_together = ['producto', 'empresa']
        ordering = ['-fecha_actualizacion']
    
    def __str__(self):
        return f"{self.producto.nombre} - {self.empresa.nombre} ({self.cantidad} unidades)"
    
    @property
    def requiere_reorden(self):
        """Verifica si el producto necesita ser reordenado"""
        return self.cantidad <= self.cantidad_minima
    
    @property
    def valor_total(self):
        """Calcula el valor total del inventario (cantidad * precio)"""
        return self.cantidad * self.producto.precio_usd


class MovimientoInventario(models.Model):
    """Modelo para registrar movimientos de inventario (entradas/salidas)"""
    
    TIPO_MOVIMIENTO_CHOICES = [
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
        ('AJUSTE', 'Ajuste'),
    ]
    
    registro_inventario = models.ForeignKey(
        RegistroInventario,
        on_delete=models.CASCADE,
        related_name='movimientos',
        verbose_name='Registro de Inventario'
    )
    tipo_movimiento = models.CharField(
        max_length=20,
        choices=TIPO_MOVIMIENTO_CHOICES,
        verbose_name='Tipo de Movimiento'
    )
    cantidad = models.IntegerField(
        verbose_name='Cantidad'
    )
    motivo = models.TextField(
        verbose_name='Motivo del Movimiento',
        blank=True
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario que Registró'
    )
    fecha_movimiento = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha del Movimiento'
    )
    hash_blockchain = models.CharField(
        max_length=66,
        verbose_name='Hash en Blockchain',
        blank=True,
        help_text='Hash de la transacción registrada en blockchain'
    )
    
    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        return f"{self.tipo_movimiento} - {self.cantidad} unidades - {self.fecha_movimiento}"