"""
Repositorios de Inventario y Movimiento - Implementación con Django ORM
Capa de Infraestructura
"""
from typing import List, Optional
from datetime import datetime
from aplicacion.interfaces.repositorios import IRepositorioInventario, IRepositorioMovimiento, IRepositorioUsuario
from dominio.entidades.inventario import RegistroInventario
from dominio.entidades.movimiento import MovimientoInventario, TipoMovimiento
from infraestructura.django_orm.models import (
    InventarioModel,
    MovimientoInventarioModel,
    UsuarioModel
)


# ============== REPOSITORIO DE INVENTARIO ==============

class RepositorioInventarioDjango(IRepositorioInventario):
    """Implementación del repositorio de Inventario usando Django ORM"""
    
    def guardar(self, inventario: RegistroInventario) -> RegistroInventario:
        """Persiste un registro de inventario"""
        inventario_model = InventarioModel(
            producto_id=inventario.producto_id,
            empresa_id=inventario.empresa_id,
            stock_actual=inventario.stock_actual,
            stock_minimo=inventario.stock_minimo,
            stock_maximo=inventario.stock_maximo,
            requiere_reorden=inventario.requiere_reorden
        )
        inventario_model.save()
        inventario.id = inventario_model.id
        return inventario
    
    def obtener_por_id(self, inventario_id: int) -> Optional[RegistroInventario]:
        """Obtiene un registro de inventario por ID"""
        try:
            modelo = InventarioModel.objects.get(id=inventario_id)
            return self._modelo_a_entidad(modelo)
        except InventarioModel.DoesNotExist:
            return None
    
    def obtener_por_producto(self, producto_id: int) -> Optional[RegistroInventario]:
        """Obtiene el registro de inventario de un producto"""
        try:
            modelo = InventarioModel.objects.get(producto_id=producto_id)
            return self._modelo_a_entidad(modelo)
        except InventarioModel.DoesNotExist:
            return None
    
    def listar_por_empresa(self, empresa_id: int) -> List[RegistroInventario]:
        """Lista todos los inventarios de una empresa"""
        modelos = InventarioModel.objects.filter(empresa_id=empresa_id)
        return [self._modelo_a_entidad(m) for m in modelos]
    
    def listar_con_stock_bajo(self, empresa_id: Optional[int] = None) -> List[RegistroInventario]:
        """Lista inventarios que requieren reorden"""
        queryset = InventarioModel.objects.filter(requiere_reorden=True)
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        return [self._modelo_a_entidad(m) for m in queryset]
    
    def listar_por_estado(self, estado: str, empresa_id: Optional[int] = None) -> List[RegistroInventario]:
        """Lista inventarios por estado (CRITICO, BAJO, NORMAL, ALTO)"""
        queryset = InventarioModel.objects.all()
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        
        # Filtrar por estado en memoria (la lógica está en la entidad)
        inventarios = [self._modelo_a_entidad(m) for m in queryset]
        return [i for i in inventarios if i.obtener_estado_stock() == estado]
    
    def actualizar(self, inventario: RegistroInventario) -> RegistroInventario:
        """Actualiza un registro de inventario"""
        modelo = InventarioModel.objects.get(id=inventario.id)
        modelo.stock_actual = inventario.stock_actual
        modelo.stock_minimo = inventario.stock_minimo
        modelo.stock_maximo = inventario.stock_maximo
        modelo.requiere_reorden = inventario.requiere_reorden
        modelo.save()
        return inventario
    
    def existe_inventario(self, producto_id: int) -> bool:
        """Verifica si existe registro de inventario para un producto"""
        return InventarioModel.objects.filter(producto_id=producto_id).exists()
    
    def _modelo_a_entidad(self, modelo: InventarioModel) -> RegistroInventario:
        """Convierte un modelo Django a entidad de dominio"""
        return RegistroInventario(
            id=modelo.id,
            producto_id=modelo.producto_id,
            empresa_id=modelo.empresa_id,
            stock_actual=modelo.stock_actual,
            stock_minimo=modelo.stock_minimo,
            stock_maximo=modelo.stock_maximo,
            requiere_reorden=modelo.requiere_reorden,
            ultima_actualizacion=modelo.ultima_actualizacion
        )


# ============== REPOSITORIO DE MOVIMIENTO ==============

class RepositorioMovimientoDjango(IRepositorioMovimiento):
    """Implementación del repositorio de Movimiento usando Django ORM"""
    
    def guardar(self, movimiento: MovimientoInventario) -> MovimientoInventario:
        """Persiste un movimiento de inventario"""
        movimiento_model = MovimientoInventarioModel(
            tipo_movimiento=movimiento.tipo_movimiento.value,
            producto_id=movimiento.producto_id,
            cantidad=movimiento.cantidad,
            empresa_id=movimiento.empresa_id,
            usuario_id=movimiento.usuario_id,
            observaciones=movimiento.observaciones
        )
        movimiento_model.save()
        movimiento.id = movimiento_model.id
        return movimiento
    
    def obtener_por_id(self, movimiento_id: int) -> Optional[MovimientoInventario]:
        """Obtiene un movimiento por ID"""
        try:
            modelo = MovimientoInventarioModel.objects.get(id=movimiento_id)
            return self._modelo_a_entidad(modelo)
        except MovimientoInventarioModel.DoesNotExist:
            return None
    
    def listar_por_producto(
        self, 
        producto_id: int, 
        limite: Optional[int] = None
    ) -> List[MovimientoInventario]:
        """Lista movimientos de un producto"""
        queryset = MovimientoInventarioModel.objects.filter(
            producto_id=producto_id
        ).order_by('-fecha_movimiento')
        
        if limite:
            queryset = queryset[:limite]
        
        return [self._modelo_a_entidad(m) for m in queryset]
    
    def listar_por_empresa(
        self, 
        empresa_id: int,
        tipo_movimiento: Optional[str] = None,
        fecha_desde: Optional[datetime] = None,
        fecha_hasta: Optional[datetime] = None
    ) -> List[MovimientoInventario]:
        """Lista movimientos de una empresa con filtros opcionales"""
        queryset = MovimientoInventarioModel.objects.filter(empresa_id=empresa_id)
        
        if tipo_movimiento:
            queryset = queryset.filter(tipo_movimiento=tipo_movimiento)
        
        if fecha_desde:
            queryset = queryset.filter(fecha_movimiento__gte=fecha_desde)
        
        if fecha_hasta:
            queryset = queryset.filter(fecha_movimiento__lte=fecha_hasta)
        
        queryset = queryset.order_by('-fecha_movimiento')
        
        return [self._modelo_a_entidad(m) for m in queryset]
    
    def listar_por_tipo(self, tipo_movimiento: str, empresa_id: Optional[int] = None) -> List[MovimientoInventario]:
        """Lista movimientos por tipo"""
        queryset = MovimientoInventarioModel.objects.filter(tipo_movimiento=tipo_movimiento)
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        return [self._modelo_a_entidad(m) for m in queryset]
    
    def contar_por_producto(self, producto_id: int) -> int:
        """Cuenta el número de movimientos de un producto"""
        return MovimientoInventarioModel.objects.filter(producto_id=producto_id).count()
    
    def _modelo_a_entidad(self, modelo: MovimientoInventarioModel) -> MovimientoInventario:
        """Convierte un modelo Django a entidad de dominio"""
        return MovimientoInventario(
            id=modelo.id,
            tipo_movimiento=TipoMovimiento(modelo.tipo_movimiento),
            producto_id=modelo.producto_id,
            cantidad=modelo.cantidad,
            empresa_id=modelo.empresa_id,
            usuario_id=modelo.usuario_id,
            observaciones=modelo.observaciones,
            fecha_movimiento=modelo.fecha_movimiento
        )


# ============== REPOSITORIO DE USUARIO ==============

class RepositorioUsuarioDjango(IRepositorioUsuario):
    """Implementación del repositorio de Usuario usando Django ORM"""
    
    def obtener_por_id(self, usuario_id: int) -> Optional[dict]:
        """Obtiene un usuario por ID"""
        try:
            modelo = UsuarioModel.objects.get(id=usuario_id)
            return {
                'id': modelo.id,
                'nombre': modelo.nombre,
                'email': modelo.email,
                'rol': modelo.rol,
                'activo': modelo.activo
            }
        except UsuarioModel.DoesNotExist:
            return None
    
    def obtener_por_email(self, email: str) -> Optional[dict]:
        """Obtiene un usuario por email"""
        try:
            modelo = UsuarioModel.objects.get(email=email)
            return {
                'id': modelo.id,
                'nombre': modelo.nombre,
                'email': modelo.email,
                'rol': modelo.rol,
                'activo': modelo.activo,
                'password': modelo.password
            }
        except UsuarioModel.DoesNotExist:
            return None
    
    def verificar_permisos(self, usuario_id: int, permiso: str) -> bool:
        """Verifica si un usuario tiene un permiso específico"""
        try:
            modelo = UsuarioModel.objects.get(id=usuario_id)
            # Los administradores tienen todos los permisos
            if modelo.rol == UsuarioModel.ROL_ADMINISTRADOR:
                return True
            # Los usuarios externos tienen permisos limitados
            return False
        except UsuarioModel.DoesNotExist:
            return False
