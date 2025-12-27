from django.db import models
from empresas.models import Empresa

class Producto(models.Model):
    """Modelo para almacenar información de productos"""
    
    codigo = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Código del Producto'
    )
    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre del Producto'
    )
    caracteristicas = models.TextField(
        verbose_name='Características',
        blank=True
    )
    precio_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio en USD',
        help_text='Precio en dólares americanos'
    )
    precio_cop = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio en COP',
        help_text='Precio en pesos colombianos',
        null=True,
        blank=True
    )
    precio_eur = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio en EUR',
        help_text='Precio en euros',
        null=True,
        blank=True
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        related_name='productos',
        verbose_name='Empresa'
    )
    imagen = models.ImageField(
        upload_to='productos/',
        verbose_name='Imagen del Producto',
        null=True,
        blank=True
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
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} - {self.codigo}"
    
    def calcular_precios_monedas(self):
        """Calcula precios en otras monedas basado en USD"""
        from decimal import Decimal
        
        # Tasas de cambio (usar Decimal en lugar de float)
        TASA_USD_A_COP = Decimal('4000')
        TASA_USD_A_EUR = Decimal('0.92')
        
        if not self.precio_cop:
            self.precio_cop = self.precio_usd * TASA_USD_A_COP
        if not self.precio_eur:
            self.precio_eur = self.precio_usd * TASA_USD_A_EUR
    
    def save(self, *args, **kwargs):
        """Override del método save para calcular precios automáticamente"""
        self.calcular_precios_monedas()
        super().save(*args, **kwargs)