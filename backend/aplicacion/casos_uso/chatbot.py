"""
Casos de Uso del Chatbot - Capa de Aplicación
Lógica de consultas del chatbot sin dependencias de Django
"""
from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
from aplicacion.interfaces.repositorios import (
    IRepositorioProducto,
    IRepositorioInventario,
    IRepositorioMovimiento
)


class ConsultarStockCasoDeUso:
    """
    Caso de uso para consultar el stock actual
    """
    
    def __init__(
        self,
        repositorio_inventario: IRepositorioInventario,
        repositorio_producto: IRepositorioProducto
    ):
        self.repo_inventario = repositorio_inventario
        self.repo_producto = repositorio_producto
    
    def ejecutar(self, producto_codigo: Optional[str] = None, limite: int = 20) -> dict:
        """
        Consulta el stock de productos
        
        Args:
            producto_codigo: Código del producto específico (opcional)
            limite: Número máximo de productos a retornar
        
        Returns:
            {
                'total_productos': int,
                'productos': [
                    {
                        'codigo': str,
                        'nombre': str,
                        'empresa': str,
                        'cantidad': int,
                        'cantidad_minima': int,
                        'requiere_reorden': bool,
                        'precio_usd': float
                    }
                ]
            }
        """
        if producto_codigo:
            # Consultar producto específico
            producto = self.repo_producto.obtener_por_codigo(producto_codigo)
            if not producto:
                return {
                    'total_productos': 0,
                    'productos': []
                }
            
            inventario = self.repo_inventario.obtener_por_producto(producto.id)
            if not inventario:
                return {
                    'total_productos': 0,
                    'productos': []
                }
            
            productos = [{
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'empresa': 'N/A',  # Se debe obtener de empresa_id
                'cantidad': inventario.stock_actual,
                'cantidad_minima': inventario.stock_minimo,
                'requiere_reorden': inventario.requiere_reorden,
                'precio_usd': float(producto.precio_usd)
            }]
        else:
            # Consultar todos los productos
            # Nota: Implementar método listar_todos en repositorio
            productos = []
        
        return {
            'total_productos': len(productos),
            'productos': productos
        }


class ObtenerProductosBajoStockCasoDeUso:
    """
    Caso de uso para obtener productos que requieren reorden
    """
    
    def __init__(
        self,
        repositorio_inventario: IRepositorioInventario,
        repositorio_producto: IRepositorioProducto  # ✅ Agregar repositorio de producto
    ):
        self.repo_inventario = repositorio_inventario
        self.repo_producto = repositorio_producto  # ✅ Guardar referencia
    
    def ejecutar(self) -> dict:
        """
        Obtiene productos con stock bajo
        
        Returns:
            {
                'total_criticos': int,
                'productos': [
                    {
                        'codigo': str,
                        'nombre': str,
                        'empresa': str,
                        'cantidad_actual': int,
                        'cantidad_minima': int,
                        'deficit': int
                    }
                ]
            }
        """
        # Obtener inventarios con stock bajo
        inventarios_bajo_stock = self.repo_inventario.listar_con_stock_bajo()
        
        productos_criticos = []
        for inventario in inventarios_bajo_stock:
            # ✅ CORREGIDO: Obtener datos reales del producto
            producto = self.repo_producto.obtener_por_id(inventario.producto_id)
            
            if producto:
                productos_criticos.append({
                    'codigo': producto.codigo,
                    'nombre': producto.nombre,
                    'empresa': inventario.empresa.nombre if hasattr(inventario, 'empresa') else 'N/A',
                    'cantidad_actual': inventario.stock_actual,
                    'cantidad_minima': inventario.stock_minimo,
                    'deficit': inventario.stock_minimo - inventario.stock_actual
                })
        
        return {
            'total_criticos': len(productos_criticos),
            'productos': productos_criticos
        }


class BuscarProductoCasoDeUso:
    """
    Caso de uso para buscar productos por nombre o código
    """
    
    def __init__(
        self,
        repositorio_producto: IRepositorioProducto,
        repositorio_inventario: IRepositorioInventario
    ):
        self.repo_producto = repositorio_producto
        self.repo_inventario = repositorio_inventario
    
    def ejecutar(self, termino: str, limite: int = 10) -> dict:
        """
        Busca productos por nombre o código
        
        Args:
            termino: Término de búsqueda
            limite: Número máximo de resultados
        
        Returns:
            {
                'total_encontrados': int,
                'productos': [
                    {
                        'codigo': str,
                        'nombre': str,
                        'descripcion': str,
                        'precio_usd': float,
                        'stock': int,
                        'tiene_stock_bajo': bool
                    }
                ]
            }
        """
        # Normalizar término (implementar en dominio)
        termino_normalizado = termino.lower().strip()
        
        # Buscar productos
        productos = self.repo_producto.buscar_por_nombre(termino_normalizado)
        
        resultados = []
        for producto in productos[:limite]:
            # Obtener inventario
            inventario = self.repo_inventario.obtener_por_producto(producto.id)
            
            resultados.append({
                'codigo': producto.codigo,
                'nombre': producto.nombre,
                'descripcion': producto.descripcion or 'Sin descripción',
                'precio_usd': float(producto.precio_usd),
                'stock': inventario.stock_actual if inventario else 0,
                'tiene_stock_bajo': inventario.requiere_reorden if inventario else False
            })
        
        return {
            'total_encontrados': len(resultados),
            'productos': resultados
        }


class ObtenerEstadisticasInventarioCasoDeUso:
    """
    Caso de uso para obtener estadísticas generales del inventario
    """
    
    def __init__(
        self,
        repositorio_inventario: IRepositorioInventario,
        repositorio_movimiento: IRepositorioMovimiento
    ):
        self.repo_inventario = repositorio_inventario
        self.repo_movimiento = repositorio_movimiento
    
    def ejecutar(self) -> dict:
        """
        Obtiene estadísticas del inventario
        
        Returns:
            {
                'total_productos': int,
                'productos_bajo_stock': int,
                'valor_total_inventario': float,
                'total_movimientos': int,
                'entradas_este_mes': int,
                'salidas_este_mes': int
            }
        """
        # Contar productos
        # Nota: Implementar métodos en repositorio
        total_productos = 0  # repo_inventario.contar_todos()
        productos_bajo_stock = 0  # repo_inventario.contar_bajo_stock()
        valor_total = 0.0  # repo_inventario.calcular_valor_total()
        
        # Contar movimientos
        total_movimientos = 0  # repo_movimiento.contar_todos()
        entradas_mes = 0  # repo_movimiento.contar_por_tipo_mes('ENTRADA')
        salidas_mes = 0  # repo_movimiento.contar_por_tipo_mes('SALIDA')
        
        return {
            'total_productos': total_productos,
            'productos_bajo_stock': productos_bajo_stock,
            'valor_total_inventario': round(valor_total, 2),
            'total_movimientos': total_movimientos,
            'entradas_este_mes': entradas_mes,
            'salidas_este_mes': salidas_mes
        }


class EnviarMensajeChatbotCasoDeUso:
    """
    Caso de uso principal del chatbot
    Orquesta la detección de intención y ejecución de acciones
    """
    
    def __init__(
        self,
        caso_uso_stock: ConsultarStockCasoDeUso,
        caso_uso_bajo_stock: ObtenerProductosBajoStockCasoDeUso,
        caso_uso_buscar: BuscarProductoCasoDeUso,
        caso_uso_estadisticas: ObtenerEstadisticasInventarioCasoDeUso
    ):
        self.caso_uso_stock = caso_uso_stock
        self.caso_uso_bajo_stock = caso_uso_bajo_stock
        self.caso_uso_buscar = caso_uso_buscar
        self.caso_uso_estadisticas = caso_uso_estadisticas
    
    def ejecutar(self, mensaje: str) -> dict:
        """
        Procesa un mensaje del usuario y genera una respuesta
        
        Args:
            mensaje: Mensaje del usuario
        
        Returns:
            {
                'respuesta': str,
                'acciones_ejecutadas': List[str],
                'datos': dict
            }
        """
        mensaje_lower = mensaje.lower()
        acciones_ejecutadas = []
        respuesta = ""
        datos = {}
        
        # Detectar intención y ejecutar caso de uso correspondiente
        
        # 1. Productos bajo stock
        if any(palabra in mensaje_lower for palabra in ['bajo', 'crítico', 'reorden', 'mínimo']):
            resultado = self.caso_uso_bajo_stock.ejecutar()
            datos = resultado
            
            if resultado['total_criticos'] > 0:
                respuesta = self._formatear_productos_bajo_stock(resultado)
            else:
                respuesta = "✅ ¡Buenas noticias! No hay productos con stock bajo."
            
            acciones_ejecutadas.append('productos_bajo_stock')
        
        # 2. Estadísticas
        elif any(palabra in mensaje_lower for palabra in ['estadística', 'total', 'resumen']):
            resultado = self.caso_uso_estadisticas.ejecutar()
            datos = resultado
            respuesta = self._formatear_estadisticas(resultado)
            acciones_ejecutadas.append('estadisticas_inventario')
        
        # 3. Buscar producto
        elif any(palabra in mensaje_lower for palabra in ['buscar', 'encuentra']):
            # Extraer término de búsqueda
            termino = self._extraer_termino_busqueda(mensaje)
            if termino:
                resultado = self.caso_uso_buscar.ejecutar(termino)
                datos = resultado
                respuesta = self._formatear_busqueda(resultado, termino)
                acciones_ejecutadas.append('buscar_producto')
            else:
                respuesta = "Para buscar, dime el nombre o código del producto."
        
        # 4. Listar inventario
        elif any(palabra in mensaje_lower for palabra in ['inventario', 'todos', 'lista']):
            resultado = self.caso_uso_stock.ejecutar()
            datos = resultado
            respuesta = self._formatear_inventario(resultado)
            acciones_ejecutadas.append('consultar_stock')
        
        # 5. Saludo
        elif any(palabra in mensaje_lower for palabra in ['hola', 'buenos', 'hey']):
            respuesta = self._mensaje_bienvenida()
        
        # 6. Default
        else:
            respuesta = self._mensaje_ayuda()
        
        return {
            'respuesta': respuesta,
            'acciones_ejecutadas': acciones_ejecutadas,
            'datos': datos
        }
    
    def _formatear_productos_bajo_stock(self, resultado: dict) -> str:
        """Formatea la respuesta de productos bajo stock"""
        productos = resultado['productos']
        respuesta = f"⚠️ Encontré {resultado['total_criticos']} producto(s) con stock bajo:\n\n"
        
        for i, p in enumerate(productos, 1):
            respuesta += f"{i}. 📦 **{p['nombre']}** ({p['codigo']})\n"
            respuesta += f"   • Stock actual: {p['cantidad_actual']} unidades\n"
            respuesta += f"   • Stock mínimo: {p['cantidad_minima']} unidades\n"
            respuesta += f"   • Déficit: {p['deficit']} unidades 🔴\n\n"
        
        respuesta += "💡 **Recomendación:** Te sugiero ordenar estos productos pronto."
        return respuesta
    
    def _formatear_estadisticas(self, resultado: dict) -> str:
        """Formatea la respuesta de estadísticas"""
        respuesta = "📊 **Estadísticas del Inventario:**\n\n"
        respuesta += f"📦 **Total de productos:** {resultado['total_productos']}\n"
        respuesta += f"⚠️ **Productos con stock bajo:** {resultado['productos_bajo_stock']}\n"
        respuesta += f"💰 **Valor total:** ${resultado['valor_total_inventario']:,.2f} USD\n\n"
        respuesta += "**Actividad de este mes:**\n"
        respuesta += f"📥 Entradas: {resultado['entradas_este_mes']}\n"
        respuesta += f"📤 Salidas: {resultado['salidas_este_mes']}\n"
        return respuesta
    
    def _formatear_busqueda(self, resultado: dict, termino: str) -> str:
        """Formatea la respuesta de búsqueda"""
        if resultado['total_encontrados'] == 0:
            return f"❌ No encontré productos que coincidan con '{termino}'."
        
        productos = resultado['productos']
        respuesta = f"🔍 Encontré {resultado['total_encontrados']} producto(s):\n\n"
        
        for i, p in enumerate(productos, 1):
            icon = "✅" if not p['tiene_stock_bajo'] else "⚠️"
            respuesta += f"{i}. {icon} **{p['nombre']}** ({p['codigo']})\n"
            respuesta += f"   • Stock: {p['stock']} unidades\n"
            respuesta += f"   • Precio: ${p['precio_usd']:.2f} USD\n\n"
        
        return respuesta
    
    def _formatear_inventario(self, resultado: dict) -> str:
        """Formatea la respuesta del inventario completo"""
        productos = resultado['productos']
        respuesta = f"📦 **Listado de Inventario** ({resultado['total_productos']} productos):\n\n"
        
        for i, p in enumerate(productos, 1):
            icon = "✅" if not p['requiere_reorden'] else "⚠️"
            respuesta += f"{i}. {icon} **{p['nombre']}** ({p['codigo']})\n"
            respuesta += f"   • Stock: {p['cantidad']} unidades\n\n"
        
        return respuesta
    
    def _extraer_termino_busqueda(self, mensaje: str) -> str:
        """Extrae el término de búsqueda del mensaje"""
        palabras_eliminar = ['buscar', 'busca', 'encuentra', 'producto', 'el', 'la']
        palabras = mensaje.lower().split()
        termino_palabras = [p for p in palabras if p not in palabras_eliminar]
        return ' '.join(termino_palabras).strip()
    
    def _mensaje_bienvenida(self) -> str:
        """Mensaje de bienvenida"""
        return ("¡Hola! 👋 Soy tu asistente de inventario.\n\n"
                "Puedo ayudarte con:\n"
                "📦 Consultar productos con stock bajo\n"
                "📊 Ver estadísticas del inventario\n"
                "🔍 Buscar productos específicos\n\n"
                "¿En qué puedo ayudarte?")
    
    def _mensaje_ayuda(self) -> str:
        """Mensaje de ayuda"""
        return ("🤔 Puedo ayudarte a:\n"
                "• Ver productos con stock bajo\n"
                "• Consultar estadísticas del inventario\n"
                "• Buscar productos específicos\n\n"
                "¿Qué te gustaría hacer?")