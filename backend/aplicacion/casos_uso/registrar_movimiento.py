"""
Caso de Uso: Registrar Movimiento de Inventario
Capa de Aplicación - Orquesta la lógica de negocio
Sin dependencias de Django, REST o infraestructura específica
"""
from typing import Dict, Any
from datetime import datetime


class RegistrarMovimientoCasoDeUso:
    """
    Caso de uso para registrar un movimiento de inventario
    
    Responsabilidades:
    - Validar que el producto exista y esté activo
    - Validar que exista inventario para el producto
    - Validar stock disponible para salidas
    - Actualizar el stock según el tipo de movimiento
    - Registrar el movimiento
    - Evaluar necesidad de reorden
    """
    
    def __init__(
        self,
        repositorio_producto,     # IRepositorioProducto
        repositorio_inventario,   # IRepositorioInventario
        repositorio_movimiento,   # IRepositorioMovimiento
        repositorio_usuario       # IRepositorioUsuario
    ):
        self.repositorio_producto = repositorio_producto
        self.repositorio_inventario = repositorio_inventario
        self.repositorio_movimiento = repositorio_movimiento
        self.repositorio_usuario = repositorio_usuario
    
    def ejecutar(self, datos_movimiento: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el caso de uso de registrar movimiento
        
        Args:
            datos_movimiento: Diccionario con datos del movimiento
                {
                    'tipo_movimiento': str (ENTRADA, SALIDA, AJUSTE, etc.),
                    'producto_id': int,
                    'cantidad': int,
                    'empresa_id': int,
                    'usuario_id': int,
                    'observaciones': str (opcional)
                }
        
        Returns:
            Dict con el movimiento registrado y el inventario actualizado
        
        Raises:
            ProductoNoEncontrado: Si el producto no existe
            ProductoInactivo: Si el producto está inactivo
            InventarioNoEncontrado: Si no existe inventario para el producto
            StockInsuficiente: Si no hay stock para una salida
            UsuarioNoEncontrado: Si el usuario no existe
        """
        from dominio.entidades.movimiento import MovimientoInventario, TipoMovimiento
        from dominio.excepciones.excepciones_negocio import (
            ProductoNoEncontrado,
            ProductoInactivo,
            InventarioNoEncontrado,
            StockInsuficiente,
            UsuarioNoEncontrado,
            DatosInvalidos
        )
        
        # 1. Validar que el producto exista y esté activo
        producto_id = datos_movimiento.get('producto_id')
        producto = self.repositorio_producto.obtener_por_id(producto_id)
        
        if not producto:
            raise ProductoNoEncontrado(producto_id)
        
        if not producto.es_activo():
            raise ProductoInactivo(producto_id)
        
        # 2. Validar que el usuario exista
        usuario_id = datos_movimiento.get('usuario_id')
        usuario = self.repositorio_usuario.obtener_por_id(usuario_id)
        
        if not usuario:
            raise UsuarioNoEncontrado(usuario_id)
        
        # 3. Obtener o crear inventario
        inventario = self.repositorio_inventario.obtener_por_producto(producto_id)
        
        if not inventario:
            raise InventarioNoEncontrado(producto_id)
        
        # 4. Validar y convertir tipo de movimiento
        try:
            tipo = TipoMovimiento(datos_movimiento['tipo_movimiento'])
        except (KeyError, ValueError) as e:
            raise DatosInvalidos(
                'tipo_movimiento',
                f"Tipo inválido. Debe ser uno de: {[t.value for t in TipoMovimiento]}"
            )
        
        # 5. Crear entidad MovimientoInventario
        try:
            movimiento = MovimientoInventario(
                tipo_movimiento=tipo,
                producto_id=producto_id,
                cantidad=datos_movimiento['cantidad'],
                empresa_id=datos_movimiento['empresa_id'],
                usuario_id=usuario_id,
                observaciones=datos_movimiento.get('observaciones', '')
            )
        except (ValueError, KeyError) as e:
            raise DatosInvalidos('movimiento', str(e))
        
        # 6. Aplicar el movimiento al inventario según el tipo
        stock_anterior = inventario.stock_actual
        
        try:
            if movimiento.es_entrada():
                # Para entradas (ENTRADA, DEVOLUCION)
                inventario.registrar_entrada(movimiento.cantidad)
                
            elif movimiento.es_salida():
                # Para salidas (SALIDA, TRANSFERENCIA)
                inventario.registrar_salida(movimiento.cantidad)
                
            elif movimiento.es_ajuste():
                # Para ajustes de inventario
                # En los ajustes, la cantidad es el nuevo stock, no un delta
                inventario.ajustar_stock(movimiento.cantidad)
                
        except ValueError as e:
            # Capturar errores específicos del dominio
            if "insuficiente" in str(e).lower():
                raise StockInsuficiente(
                    producto_id=producto_id,
                    stock_disponible=inventario.stock_actual,
                    stock_requerido=movimiento.cantidad
                )
            raise DatosInvalidos('movimiento', str(e))
        
        # 7. Persistir el inventario actualizado
        inventario_actualizado = self.repositorio_inventario.actualizar(inventario)
        
        # 8. Persistir el movimiento
        movimiento_guardado = self.repositorio_movimiento.guardar(movimiento)
        
        # 9. Construir respuesta con información completa
        resultado = {
            'movimiento': movimiento_guardado.to_dict(),
            'inventario': inventario_actualizado.to_dict(),
            'producto': {
                'id': producto.id,
                'codigo': producto.codigo,
                'nombre': producto.nombre
            },
            'stock': {
                'anterior': stock_anterior,
                'actual': inventario_actualizado.stock_actual,
                'diferencia': inventario_actualizado.stock_actual - stock_anterior
            },
            'alertas': self._generar_alertas(inventario_actualizado),
            'mensaje': self._generar_mensaje_exito(movimiento_guardado, inventario_actualizado)
        }
        
        return resultado
    
    def _generar_alertas(self, inventario) -> list:
        """
        Genera alertas basadas en el estado del inventario
        """
        alertas = []
        
        estado = inventario.obtener_estado_stock()
        
        if estado == "CRITICO":
            alertas.append({
                'tipo': 'CRITICO',
                'mensaje': f'Stock crítico: {inventario.stock_actual} unidades (mínimo: {inventario.stock_minimo})'
            })
        elif estado == "BAJO":
            alertas.append({
                'tipo': 'ADVERTENCIA',
                'mensaje': f'Stock bajo: {inventario.stock_actual} unidades'
            })
        
        if inventario.requiere_reorden:
            alertas.append({
                'tipo': 'REORDEN',
                'mensaje': 'Se requiere reabastecimiento'
            })
        
        porcentaje = float(inventario.obtener_porcentaje_stock())
        if porcentaje > 90:
            alertas.append({
                'tipo': 'INFO',
                'mensaje': f'Stock alto: {porcentaje:.1f}% del máximo'
            })
        
        return alertas
    
    def _generar_mensaje_exito(self, movimiento, inventario) -> str:
        """
        Genera un mensaje descriptivo del movimiento realizado
        """
        tipo = movimiento.tipo_movimiento.value
        cantidad = movimiento.cantidad
        stock_actual = inventario.stock_actual
        
        return (
            f'{tipo} de {cantidad} unidades registrado exitosamente. '
            f'Stock actual: {stock_actual} unidades.'
        )
