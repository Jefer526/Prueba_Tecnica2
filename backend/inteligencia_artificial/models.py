from django.db import models
from productos.models import Producto
from autenticacion.models import Usuario

class PrediccionPrecio(models.Model):
    """Modelo para almacenar predicciones de precios generadas por IA"""
    
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='predicciones_precio',
        verbose_name='Producto'
    )
    precio_actual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio Actual'
    )
    precio_predicho_30_dias = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio Predicho 30 días',
        null=True,
        blank=True
    )
    precio_predicho_60_dias = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio Predicho 60 días',
        null=True,
        blank=True
    )
    precio_predicho_90_dias = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Precio Predicho 90 días',
        null=True,
        blank=True
    )
    tendencia = models.CharField(
        max_length=20,
        choices=[
            ('ALZA', 'Alza'),
            ('BAJA', 'Baja'),
            ('ESTABLE', 'Estable'),
        ],
        verbose_name='Tendencia'
    )
    confianza_prediccion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Confianza de la Predicción (%)',
        help_text='Porcentaje de confianza del modelo (0-100)'
    )
    factores_considerados = models.JSONField(
        verbose_name='Factores Considerados',
        default=dict,
        help_text='Factores que influyeron en la predicción'
    )
    fecha_prediccion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Predicción'
    )
    modelo_utilizado = models.CharField(
        max_length=100,
        verbose_name='Modelo Utilizado',
        default='GPT-4'
    )
    
    class Meta:
        verbose_name = 'Predicción de Precio'
        verbose_name_plural = 'Predicciones de Precios'
        ordering = ['-fecha_prediccion']
    
    def __str__(self):
        return f"Predicción para {self.producto.nombre} - {self.tendencia}"


class ConsultaChatbot(models.Model):
    """Modelo para almacenar consultas al chatbot de IA"""
    
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name='consultas_chatbot',
        verbose_name='Usuario'
    )
    pregunta = models.TextField(
        verbose_name='Pregunta'
    )
    respuesta = models.TextField(
        verbose_name='Respuesta'
    )
    contexto = models.JSONField(
        verbose_name='Contexto',
        default=dict,
        help_text='Información contextual utilizada para generar la respuesta'
    )
    fecha_consulta = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Consulta'
    )
    tiempo_respuesta = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name='Tiempo de Respuesta (segundos)',
        null=True,
        blank=True
    )
    satisfaccion_usuario = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        null=True,
        blank=True,
        verbose_name='Satisfacción del Usuario (1-5)'
    )
    
    class Meta:
        verbose_name = 'Consulta de Chatbot'
        verbose_name_plural = 'Consultas de Chatbot'
        ordering = ['-fecha_consulta']
    
    def __str__(self):
        return f"Consulta de {self.usuario} - {self.fecha_consulta}"


class AnalisisInventario(models.Model):
    """Modelo para almacenar análisis de inventario generados por IA"""
    
    fecha_analisis = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Análisis'
    )
    productos_analizados = models.IntegerField(
        verbose_name='Productos Analizados'
    )
    recomendaciones = models.JSONField(
        verbose_name='Recomendaciones',
        default=list,
        help_text='Lista de recomendaciones generadas por IA'
    )
    productos_bajo_stock = models.JSONField(
        verbose_name='Productos Bajo Stock',
        default=list
    )
    productos_sobrestock = models.JSONField(
        verbose_name='Productos con Sobrestock',
        default=list
    )
    proyeccion_demanda = models.JSONField(
        verbose_name='Proyección de Demanda',
        default=dict
    )
    ahorro_potencial = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Ahorro Potencial (USD)',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Análisis de Inventario'
        verbose_name_plural = 'Análisis de Inventario'
        ordering = ['-fecha_analisis']
    
    def __str__(self):
        return f"Análisis - {self.fecha_analisis}"