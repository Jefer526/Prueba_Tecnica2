from django.db import models

class Empresa(models.Model):
    """Modelo para almacenar información de empresas"""
    
    nit = models.CharField(
        max_length=20,
        primary_key=True,
        verbose_name='NIT',
        help_text='Número de Identificación Tributaria'
    )
    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre de la Empresa'
    )
    direccion = models.CharField(
        max_length=500,
        verbose_name='Dirección'
    )
    telefono = models.CharField(
        max_length=20,
        verbose_name='Teléfono'
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
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.nit})"
    
    def total_productos(self):
        """Retorna el total de productos de la empresa"""
        return self.productos.filter(activo=True).count()
    
    def valor_total_inventario(self):
        """Calcula el valor total del inventario de la empresa"""
        from productos.models import Producto
        productos = Producto.objects.filter(empresa=self, activo=True)
        total = sum(p.precio_usd for p in productos)
        return total