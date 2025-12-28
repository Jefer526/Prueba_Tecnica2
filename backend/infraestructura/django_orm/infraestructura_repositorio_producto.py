"""
Repositorio de Producto - Implementación con Django ORM
Capa de Infraestructura
"""
from typing import List, Optional
from decimal import Decimal
from aplicacion.interfaces.repositorios import IRepositorioProducto
from dominio.entidades.producto import Producto, CategoriaProducto
from infraestructura.django_orm.models import ProductoModel


class RepositorioProductoDjango(IRepositorioProducto):
    """Implementación del repositorio de Producto usando Django ORM"""
    
    def guardar(self, producto: Producto) -> Producto:
        """Persiste un producto en la BD"""
        producto_model = ProductoModel(
            codigo=producto.codigo,
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            precio_usd=producto.precio_usd,
            precio_cop=producto.precio_cop,
            precio_eur=producto.precio_eur,
            categoria=producto.categoria.value,
            empresa_id=producto.empresa_id,
            activo=producto.activo
        )
        producto_model.save()
        producto.id = producto_model.id
        return producto
    
    def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        """Obtiene un producto por ID"""
        try:
            modelo = ProductoModel.objects.get(id=producto_id)
            return self._modelo_a_entidad(modelo)
        except ProductoModel.DoesNotExist:
            return None
    
    def obtener_por_codigo(self, codigo: str) -> Optional[Producto]:
        """Obtiene un producto por código"""
        try:
            modelo = ProductoModel.objects.get(codigo=codigo)
            return self._modelo_a_entidad(modelo)
        except ProductoModel.DoesNotExist:
            return None
    
    def listar_por_empresa(self, empresa_id: int, solo_activos: bool = True) -> List[Producto]:
        """Lista productos de una empresa"""
        queryset = ProductoModel.objects.filter(empresa_id=empresa_id)
        if solo_activos:
            queryset = queryset.filter(activo=True)
        return [self._modelo_a_entidad(p) for p in queryset]
    
    def listar_por_categoria(self, categoria: str, solo_activos: bool = True) -> List[Producto]:
        """Lista productos de una categoría"""
        queryset = ProductoModel.objects.filter(categoria=categoria)
        if solo_activos:
            queryset = queryset.filter(activo=True)
        return [self._modelo_a_entidad(p) for p in queryset]
    
    def buscar_por_nombre(self, termino: str, empresa_id: Optional[int] = None) -> List[Producto]:
        """Busca productos por nombre"""
        queryset = ProductoModel.objects.filter(nombre__icontains=termino)
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        return [self._modelo_a_entidad(p) for p in queryset]
    
    def existe_codigo(self, codigo: str, excluir_id: Optional[int] = None) -> bool:
        """Verifica si existe un código"""
        queryset = ProductoModel.objects.filter(codigo=codigo)
        if excluir_id:
            queryset = queryset.exclude(id=excluir_id)
        return queryset.exists()
    
    def obtener_siguiente_numero_codigo(self, prefijo: str) -> int:
        """Obtiene el siguiente número para un prefijo"""
        ultimo = ProductoModel.objects.filter(
            codigo__startswith=prefijo
        ).order_by('-codigo').first()
        
        if not ultimo:
            return 1
        
        try:
            # Extraer número del código (después del prefijo de 2 letras)
            numero = int(ultimo.codigo[2:])
            return numero + 1
        except (ValueError, IndexError):
            return 1
    
    def actualizar(self, producto: Producto) -> Producto:
        """Actualiza un producto existente"""
        modelo = ProductoModel.objects.get(id=producto.id)
        modelo.nombre = producto.nombre
        modelo.descripcion = producto.descripcion
        modelo.precio_usd = producto.precio_usd
        modelo.precio_cop = producto.precio_cop
        modelo.precio_eur = producto.precio_eur
        modelo.categoria = producto.categoria.value
        modelo.activo = producto.activo
        modelo.save()
        return producto
    
    def eliminar(self, producto_id: int) -> bool:
        """Elimina (soft delete) un producto"""
        try:
            modelo = ProductoModel.objects.get(id=producto_id)
            modelo.activo = False
            modelo.save()
            return True
        except ProductoModel.DoesNotExist:
            return False
    
    def _modelo_a_entidad(self, modelo: ProductoModel) -> Producto:
        """Convierte un modelo Django a entidad de dominio"""
        return Producto(
            id=modelo.id,
            codigo=modelo.codigo,
            nombre=modelo.nombre,
            descripcion=modelo.descripcion,
            precio_usd=Decimal(str(modelo.precio_usd)),
            precio_cop=Decimal(str(modelo.precio_cop)),
            precio_eur=Decimal(str(modelo.precio_eur)),
            categoria=CategoriaProducto(modelo.categoria),
            empresa_id=modelo.empresa_id,
            activo=modelo.activo,
            fecha_creacion=modelo.fecha_creacion,
            fecha_actualizacion=modelo.fecha_actualizacion
        )
