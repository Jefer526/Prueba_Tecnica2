"""
Caso de Uso: Crear Producto
Capa de Aplicación - Orquesta la lógica de negocio
Sin dependencias de Django, REST o infraestructura específica
"""
from typing import Dict, Any
from decimal import Decimal


class CrearProductoCasoDeUso:
    """
    Caso de uso para crear un nuevo producto
    
    Responsabilidades:
    - Validar que la empresa exista y esté activa
    - Generar código único del producto
    - Calcular precios en múltiples monedas
    - Crear registro de inventario inicial
    - Persistir producto e inventario
    """
    
    def __init__(
        self,
        repositorio_producto,  # IRepositorioProducto
        repositorio_empresa,   # IRepositorioEmpresa
        repositorio_inventario # IRepositorioInventario
    ):
        self.repositorio_producto = repositorio_producto
        self.repositorio_empresa = repositorio_empresa
        self.repositorio_inventario = repositorio_inventario
    
    def ejecutar(self, datos_producto: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el caso de uso de crear producto
        
        Args:
            datos_producto: Diccionario con datos del producto
                {
                    'nombre': str,
                    'descripcion': str,
                    'precio_usd': Decimal,
                    'categoria': str,
                    'empresa_id': int,
                    'stock_minimo': int,
                    'stock_maximo': int,
                    'stock_inicial': int (opcional, default 0)
                }
        
        Returns:
            Dict con el producto creado y su inventario
        
        Raises:
            EmpresaNoEncontrada: Si la empresa no existe
            EmpresaInactiva: Si la empresa está inactiva
            DatosInvalidos: Si los datos del producto son inválidos
        """
        from dominio.entidades.empresa import Empresa
        from dominio.entidades.producto import Producto, CategoriaProducto
        from dominio.entidades.inventario import RegistroInventario
        from dominio.excepciones.excepciones_negocio import (
            EmpresaNoEncontrada,
            EmpresaInactiva,
            DatosInvalidos
        )
        
        # 1. Validar que la empresa exista y esté activa
        empresa_id = datos_producto.get('empresa_id')
        empresa = self.repositorio_empresa.obtener_por_id(empresa_id)
        
        if not empresa:
            raise EmpresaNoEncontrada(empresa_id)
        
        if not empresa.es_activa():
            raise EmpresaInactiva(empresa_id)
        
        # 2. Validar y convertir categoría
        try:
            categoria = CategoriaProducto(datos_producto['categoria'])
        except (KeyError, ValueError) as e:
            raise DatosInvalidos(
                'categoria',
                f"Categoría inválida. Debe ser una de: {[c.value for c in CategoriaProducto]}"
            )
        
        # 3. Generar código único del producto
        prefijo = self._obtener_prefijo_categoria(categoria)
        siguiente_numero = self.repositorio_producto.obtener_siguiente_numero_codigo(prefijo)
        
        # 4. Crear entidad Producto
        try:
            producto = Producto(
                nombre=datos_producto['nombre'],
                descripcion=datos_producto['descripcion'],
                precio_usd=Decimal(str(datos_producto['precio_usd'])),
                categoria=categoria,
                empresa_id=empresa_id
            )
            
            # Generar código
            producto.generar_codigo(prefijo, siguiente_numero)
            
        except (ValueError, KeyError) as e:
            raise DatosInvalidos('producto', str(e))
        
        # 5. Persistir producto
        producto_guardado = self.repositorio_producto.guardar(producto)
        
        # 6. Crear registro de inventario inicial
        stock_inicial = datos_producto.get('stock_inicial', 0)
        stock_minimo = datos_producto.get('stock_minimo', 10)
        stock_maximo = datos_producto.get('stock_maximo', 100)
        
        try:
            inventario = RegistroInventario(
                producto_id=producto_guardado.id,
                stock_actual=stock_inicial,
                stock_minimo=stock_minimo,
                stock_maximo=stock_maximo,
                empresa_id=empresa_id
            )
        except ValueError as e:
            # Si falla la creación del inventario, deberíamos hacer rollback del producto
            # Esto se manejaría con transacciones en la capa de infraestructura
            raise DatosInvalidos('inventario', str(e))
        
        # 7. Persistir inventario
        inventario_guardado = self.repositorio_inventario.guardar(inventario)
        
        # 8. Retornar resultado
        return {
            'producto': producto_guardado.to_dict(),
            'inventario': inventario_guardado.to_dict(),
            'mensaje': f'Producto {producto_guardado.codigo} creado exitosamente'
        }
    
    def _obtener_prefijo_categoria(self, categoria: 'CategoriaProducto') -> str:
        """
        Obtiene el prefijo de código según la categoría
        Regla de negocio: cada categoría tiene un prefijo específico
        """
        from dominio.entidades.producto import CategoriaProducto
        
        prefijos = {
            CategoriaProducto.TECNOLOGIA: 'TE',
            CategoriaProducto.OFICINA: 'OF',
            CategoriaProducto.CONSUMIBLES: 'CO',
            CategoriaProducto.EQUIPAMIENTO: 'EQ',
            CategoriaProducto.OTROS: 'OT'
        }
        
        return prefijos.get(categoria, 'PO')
