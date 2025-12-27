import json
from typing import List, Dict, Any
from django.conf import settings
from django.db import models
from django.utils import timezone

from inventario.models import RegistroInventario, MovimientoInventario
from productos.models import Producto
from empresas.models import Empresa


class ChatbotService:
    """Servicio para chatbot local sin API externa"""
    
    def __init__(self):
        self.model = "chatbot-local-v1"
    
    def consultar_stock(self, producto_codigo: str = None) -> Dict[str, Any]:
        """Consulta el stock de productos"""
        try:
            if producto_codigo:
                registros = RegistroInventario.objects.filter(
                    producto__codigo=producto_codigo,
                    activo=True
                ).select_related('producto', 'empresa')
            else:
                registros = RegistroInventario.objects.filter(
                    activo=True
                ).select_related('producto', 'empresa')[:20]
            
            productos = []
            for reg in registros:
                productos.append({
                    'codigo': reg.producto.codigo,
                    'nombre': reg.producto.nombre,
                    'empresa': reg.empresa.nombre,
                    'cantidad': reg.cantidad,
                    'cantidad_minima': reg.cantidad_minima,
                    'requiere_reorden': reg.requiere_reorden,
                    'ubicacion': reg.ubicacion_bodega or 'N/A',
                    'precio_usd': float(reg.producto.precio_usd)
                })
            
            return {
                'exito': True,
                'total_productos': len(productos),
                'productos': productos
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }
    
    def productos_bajo_stock(self) -> Dict[str, Any]:
        """Obtiene productos que requieren reorden"""
        try:
            registros = RegistroInventario.objects.filter(
                activo=True
            ).select_related('producto', 'empresa')
            
            productos_criticos = []
            for reg in registros:
                if reg.requiere_reorden:
                    productos_criticos.append({
                        'codigo': reg.producto.codigo,
                        'nombre': reg.producto.nombre,
                        'empresa': reg.empresa.nombre,
                        'cantidad_actual': reg.cantidad,
                        'cantidad_minima': reg.cantidad_minima,
                        'deficit': reg.cantidad_minima - reg.cantidad,
                        'ubicacion': reg.ubicacion_bodega or 'N/A'
                    })
            
            return {
                'exito': True,
                'total_criticos': len(productos_criticos),
                'productos': productos_criticos
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }
    
    def buscar_producto(self, termino: str) -> Dict[str, Any]:
        """Busca productos por nombre o código"""
        try:
            productos = Producto.objects.filter(
                activo=True
            ).filter(
                models.Q(nombre__icontains=termino) |
                models.Q(codigo__icontains=termino)
            )[:10]
            
            resultados = []
            for prod in productos:
                registro = RegistroInventario.objects.filter(
                    producto=prod,
                    activo=True
                ).first()
                
                resultados.append({
                    'codigo': prod.codigo,
                    'nombre': prod.nombre,
                    'descripcion': prod.descripcion or 'Sin descripción',
                    'precio_usd': float(prod.precio_usd),
                    'stock': registro.cantidad if registro else 0,
                    'tiene_stock_bajo': registro.requiere_reorden if registro else False
                })
            
            return {
                'exito': True,
                'total_encontrados': len(resultados),
                'productos': resultados
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }
    
    def historial_movimientos(self, producto_codigo: str, limite: int = 10) -> Dict[str, Any]:
        """Obtiene el historial de movimientos de un producto"""
        try:
            movimientos = MovimientoInventario.objects.filter(
                registro_inventario__producto__codigo=producto_codigo
            ).select_related(
                'registro_inventario__producto',
                'usuario'
            ).order_by('-fecha_movimiento')[:limite]
            
            historial = []
            for mov in movimientos:
                historial.append({
                    'fecha': mov.fecha_movimiento.strftime('%Y-%m-%d %H:%M'),
                    'tipo': mov.tipo_movimiento,
                    'cantidad': mov.cantidad,
                    'usuario': mov.usuario.nombre_completo if mov.usuario else 'Sistema',
                    'motivo': mov.motivo or 'Sin motivo especificado'
                })
            
            return {
                'exito': True,
                'producto_codigo': producto_codigo,
                'total_movimientos': len(historial),
                'movimientos': historial
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }
    
    def estadisticas_inventario(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del inventario"""
        try:
            total_productos = RegistroInventario.objects.filter(activo=True).count()
            productos_bajo_stock = RegistroInventario.objects.filter(
                activo=True,
                cantidad__lte=models.F('cantidad_minima')
            ).count()
            
            valor_total = sum([
                reg.cantidad * float(reg.producto.precio_usd)
                for reg in RegistroInventario.objects.filter(activo=True).select_related('producto')
            ])
            
            total_movimientos = MovimientoInventario.objects.count()
            entradas_mes = MovimientoInventario.objects.filter(
                tipo_movimiento='ENTRADA',
                fecha_movimiento__month=timezone.now().month
            ).count()
            salidas_mes = MovimientoInventario.objects.filter(
                tipo_movimiento='SALIDA',
                fecha_movimiento__month=timezone.now().month
            ).count()
            
            return {
                'exito': True,
                'estadisticas': {
                    'total_productos': total_productos,
                    'productos_bajo_stock': productos_bajo_stock,
                    'valor_total_inventario': round(valor_total, 2),
                    'total_movimientos': total_movimientos,
                    'entradas_este_mes': entradas_mes,
                    'salidas_este_mes': salidas_mes
                }
            }
        except Exception as e:
            return {
                'exito': False,
                'error': str(e)
            }
    
    def ejecutar_funcion(self, nombre_funcion: str, argumentos: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta una función del sistema según el nombre"""
        funciones = {
            'consultar_stock': self.consultar_stock,
            'productos_bajo_stock': self.productos_bajo_stock,
            'buscar_producto': self.buscar_producto,
            'historial_movimientos': self.historial_movimientos,
            'estadisticas_inventario': self.estadisticas_inventario,
        }
        
        if nombre_funcion in funciones:
            args_limpios = {k: v for k, v in argumentos.items() if v is not None}
            return funciones[nombre_funcion](**args_limpios)
        else:
            return {
                'exito': False,
                'error': f'Función {nombre_funcion} no encontrada'
            }
    
    def generar_respuesta(self, mensajes: List[Dict[str, str]]) -> Dict[str, Any]:
        """Genera respuesta usando lógica local (detección de palabras clave)"""
        try:
            # Obtener último mensaje del usuario
            contenido_usuario = mensajes[-1]['content'].lower() if mensajes else ""
            
            acciones_ejecutadas = []
            respuesta_final = ""
            
            # DETECCIÓN INTELIGENTE DE INTENCIONES (ORDEN IMPORTANTE)
            
            # 1. STOCK BAJO (máxima prioridad)
            if any(palabra in contenido_usuario for palabra in ['bajo', 'bajos', 'crítico', 'críticos', 'reorden', 'falta', 'mínimo']):
                resultado = self.productos_bajo_stock()
                if resultado['exito']:
                    if resultado['total_criticos'] > 0:
                        productos = resultado['productos']
                        respuesta_final = f"⚠️ Encontré {resultado['total_criticos']} producto(s) con stock bajo:\n\n"
                        for i, p in enumerate(productos, 1):
                            respuesta_final += f"{i}. 📦 **{p['nombre']}** ({p['codigo']})\n"
                            respuesta_final += f"   • Empresa: {p['empresa']}\n"
                            respuesta_final += f"   • Stock actual: {p['cantidad_actual']} unidades\n"
                            respuesta_final += f"   • Stock mínimo: {p['cantidad_minima']} unidades\n"
                            respuesta_final += f"   • Déficit: {p['deficit']} unidades 🔴\n"
                            respuesta_final += f"   • Ubicación: {p['ubicacion']}\n\n"
                        respuesta_final += "💡 **Recomendación:** Te sugiero ordenar estos productos pronto."
                        acciones_ejecutadas.append('productos_bajo_stock')
                    else:
                        respuesta_final = "✅ ¡Buenas noticias! No hay productos con stock bajo en este momento."
                        acciones_ejecutadas.append('productos_bajo_stock')
            
            # 2. ESTADÍSTICAS
            elif any(palabra in contenido_usuario for palabra in ['estadística', 'estadísticas', 'total', 'cuánto', 'cuantos', 'resumen']):
                resultado = self.estadisticas_inventario()
                if resultado['exito']:
                    stats = resultado['estadisticas']
                    respuesta_final = "📊 **Estadísticas del Inventario:**\n\n"
                    respuesta_final += f"📦 **Total de productos:** {stats['total_productos']}\n"
                    respuesta_final += f"⚠️ **Productos con stock bajo:** {stats['productos_bajo_stock']}\n"
                    respuesta_final += f"💰 **Valor total:** ${stats['valor_total_inventario']:,.2f} USD\n"
                    respuesta_final += f"📝 **Total de movimientos:** {stats['total_movimientos']}\n\n"
                    respuesta_final += "**Actividad de este mes:**\n"
                    respuesta_final += f"📥 Entradas: {stats['entradas_este_mes']}\n"
                    respuesta_final += f"📤 Salidas: {stats['salidas_este_mes']}\n"
                    acciones_ejecutadas.append('estadisticas_inventario')
            
            # 3. BUSCAR PRODUCTO ESPECÍFICO (CORREGIDO)
            elif any(palabra in contenido_usuario for palabra in ['buscar', 'busca', 'encuentra']):
                # Palabras a eliminar del término de búsqueda
                palabras_eliminar = ['buscar', 'busca', 'encuentra', 'producto', 'el', 'la', 'los', 'las', 'un', 'una', 'me', 'por', 'favor']
                
                # Dividir en palabras y filtrar
                palabras = contenido_usuario.split()
                termino_palabras = [p for p in palabras if p not in palabras_eliminar]
                termino = ' '.join(termino_palabras).strip()
                
                if termino:
                    resultado = self.buscar_producto(termino)
                    if resultado['exito'] and resultado['total_encontrados'] > 0:
                        productos = resultado['productos']
                        respuesta_final = f"🔍 Encontré {resultado['total_encontrados']} producto(s) que coinciden con '{termino}':\n\n"
                        for i, p in enumerate(productos, 1):
                            stock_icon = "✅" if p['stock'] > 0 and not p['tiene_stock_bajo'] else "⚠️"
                            respuesta_final += f"{i}. {stock_icon} **{p['nombre']}** ({p['codigo']})\n"
                            respuesta_final += f"   • Stock disponible: {p['stock']} unidades\n"
                            respuesta_final += f"   • Precio: ${p['precio_usd']:.2f} USD\n"
                            respuesta_final += f"   • Descripción: {p['descripcion']}\n"
                            if p['tiene_stock_bajo']:
                                respuesta_final += f"   • ⚠️ **Stock bajo - Requiere reorden**\n"
                            respuesta_final += "\n"
                        acciones_ejecutadas.append('buscar_producto')
                    else:
                        respuesta_final = f"❌ No encontré productos que coincidan con '{termino}'.\n\n" \
                                        "Intenta con otro nombre o código de producto."
                else:
                    respuesta_final = "Para buscar un producto, dime su nombre o código.\n\n" \
                                    "Por ejemplo: 'Buscar laptop' o 'Buscar PO001'"
            
            # 4. CONSULTAR TODO EL INVENTARIO
            elif any(palabra in contenido_usuario for palabra in ['inventario', 'todos', 'lista']):
                resultado = self.consultar_stock()
                if resultado['exito']:
                    productos = resultado['productos']
                    respuesta_final = f"📦 **Listado de Inventario** ({resultado['total_productos']} productos):\n\n"
                    for i, p in enumerate(productos, 1):
                        stock_icon = "✅" if not p['requiere_reorden'] else "⚠️"
                        respuesta_final += f"{i}. {stock_icon} **{p['nombre']}** ({p['codigo']})\n"
                        respuesta_final += f"   • Stock: {p['cantidad']} unidades (mín: {p['cantidad_minima']})\n"
                        respuesta_final += f"   • Empresa: {p['empresa']}\n"
                        respuesta_final += f"   • Ubicación: {p['ubicacion']}\n\n"
                    acciones_ejecutadas.append('consultar_stock')
            
            # 5. SALUDOS
            elif any(palabra in contenido_usuario for palabra in ['hola', 'buenos', 'buenas', 'hey', 'qué tal']):
                respuesta_final = "¡Hola! 👋 Soy tu asistente de inventario.\n\n" \
                                "Puedo ayudarte con:\n" \
                                "📦 Consultar productos con stock bajo\n" \
                                "📊 Ver estadísticas del inventario\n" \
                                "🔍 Buscar productos específicos\n" \
                                "📈 Revisar el listado completo\n\n" \
                                "¿En qué puedo ayudarte?"
            
            # 6. RESPUESTA POR DEFECTO
            else:
                respuesta_final = "🤔 No estoy seguro de cómo ayudarte con eso.\n\n" \
                                "Puedo ayudarte a:\n" \
                                "• Ver productos con stock bajo\n" \
                                "• Consultar estadísticas del inventario\n" \
                                "• Buscar productos específicos\n\n" \
                                "¿Qué te gustaría hacer?"
            
            return {
                'exito': True,
                'respuesta': respuesta_final,
                'acciones_ejecutadas': acciones_ejecutadas,
                'tokens_usados': 0
            }
            
        except Exception as e:
            return {
                'exito': False,
                'error': f'Error al generar respuesta: {str(e)}',
                'respuesta': 'Lo siento, ha ocurrido un error al procesar tu consulta. Por favor, intenta de nuevo.'
            }