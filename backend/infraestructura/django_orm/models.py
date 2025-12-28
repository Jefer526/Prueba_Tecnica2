"""
Models de Django - Capa de Infraestructura
Solo para PERSISTENCIA - Sin lógica de negocio
"""
from django.db import models


class EmpresaModel(models.Model):
    """Modelo de persistencia para Empresa"""
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    nit = models.CharField(max_length=20, unique=True, verbose_name='NIT')
    direccion = models.TextField(verbose_name='Dirección')
    telefono = models.CharField(max_length=20, verbose_name='Teléfono')
    email = models.EmailField(verbose_name='Email')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        db_table = 'empresas'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} ({self.nit})"


class ProductoModel(models.Model):
    """Modelo de persistencia para Producto"""
    codigo = models.CharField(max_length=10, unique=True, verbose_name='Código')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    descripcion = models.TextField(verbose_name='Descripción')
    precio_usd = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio USD')
    precio_cop = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio COP')
    precio_eur = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio EUR')
    categoria = models.CharField(max_length=20, verbose_name='Categoría')
    empresa = models.ForeignKey(
        EmpresaModel, 
        on_delete=models.CASCADE,
        related_name='productos',
        verbose_name='Empresa'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        db_table = 'productos'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['codigo']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class InventarioModel(models.Model):
    """Modelo de persistencia para Inventario"""
    producto = models.OneToOneField(
        ProductoModel,
        on_delete=models.CASCADE,
        related_name='inventario',
        verbose_name='Producto'
    )
    empresa = models.ForeignKey(
        EmpresaModel,
        on_delete=models.CASCADE,
        related_name='inventarios',
        verbose_name='Empresa'
    )
    stock_actual = models.IntegerField(default=0, verbose_name='Stock Actual')
    stock_minimo = models.IntegerField(default=10, verbose_name='Stock Mínimo')
    stock_maximo = models.IntegerField(default=100, verbose_name='Stock Máximo')
    requiere_reorden = models.BooleanField(default=False, verbose_name='Requiere Reorden')
    ultima_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        db_table = 'inventarios'
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'
        ordering = ['producto__codigo']
    
    def __str__(self):
        return f"Inventario de {self.producto.codigo}"


class MovimientoInventarioModel(models.Model):
    """Modelo de persistencia para MovimientoInventario"""
    tipo_movimiento = models.CharField(max_length=20, verbose_name='Tipo de Movimiento')
    producto = models.ForeignKey(
        ProductoModel,
        on_delete=models.CASCADE,
        related_name='movimientos',
        verbose_name='Producto'
    )
    cantidad = models.IntegerField(verbose_name='Cantidad')
    empresa = models.ForeignKey(
        EmpresaModel,
        on_delete=models.CASCADE,
        related_name='movimientos',
        verbose_name='Empresa'
    )
    usuario_id = models.IntegerField(verbose_name='Usuario ID')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    fecha_movimiento = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Movimiento')
    
    class Meta:
        db_table = 'movimientos_inventario'
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha_movimiento']
    
    def __str__(self):
        return f"{self.tipo_movimiento} - {self.producto.codigo} ({self.cantidad})"


class UsuarioModel(models.Model):
    """Modelo de persistencia para Usuario"""
    ROL_ADMINISTRADOR = 'ADMINISTRADOR'
    ROL_EXTERNO = 'EXTERNO'
    
    ROLES = [
        (ROL_ADMINISTRADOR, 'Administrador'),
        (ROL_EXTERNO, 'Usuario Externo'),
    ]
    
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    email = models.EmailField(unique=True, verbose_name='Email')
    password = models.CharField(max_length=255, verbose_name='Contraseña')
    rol = models.CharField(max_length=20, choices=ROLES, verbose_name='Rol')
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.nombre} ({self.email})"
