"""
Excepciones del Dominio
Excepciones específicas para errores de reglas de negocio
Sin dependencias de Django o infraestructura
"""


class ExcepcionDominio(Exception):
    """Excepción base para todos los errores de dominio"""
    def __init__(self, mensaje: str, codigo_error: str = None):
        self.mensaje = mensaje
        self.codigo_error = codigo_error or self.__class__.__name__
        super().__init__(self.mensaje)


# === EXCEPCIONES DE PRODUCTO ===

class ProductoNoEncontrado(ExcepcionDominio):
    """Se lanza cuando un producto no existe"""
    def __init__(self, producto_id: int):
        super().__init__(
            mensaje=f"El producto con ID {producto_id} no fue encontrado",
            codigo_error="PRODUCTO_NO_ENCONTRADO"
        )


class ProductoInactivo(ExcepcionDominio):
    """Se lanza cuando se intenta operar con un producto inactivo"""
    def __init__(self, producto_id: int):
        super().__init__(
            mensaje=f"El producto con ID {producto_id} está inactivo",
            codigo_error="PRODUCTO_INACTIVO"
        )


class CodigoProductoDuplicado(ExcepcionDominio):
    """Se lanza cuando se intenta crear un producto con código duplicado"""
    def __init__(self, codigo: str):
        super().__init__(
            mensaje=f"Ya existe un producto con el código {codigo}",
            codigo_error="CODIGO_DUPLICADO"
        )


class PrecioInvalido(ExcepcionDominio):
    """Se lanza cuando el precio de un producto es inválido"""
    def __init__(self, precio: float, razon: str = ""):
        mensaje = f"Precio inválido: {precio}"
        if razon:
            mensaje += f". {razon}"
        super().__init__(mensaje=mensaje, codigo_error="PRECIO_INVALIDO")


# === EXCEPCIONES DE INVENTARIO ===

class InventarioNoEncontrado(ExcepcionDominio):
    """Se lanza cuando no existe registro de inventario para un producto"""
    def __init__(self, producto_id: int):
        super().__init__(
            mensaje=f"No existe registro de inventario para el producto {producto_id}",
            codigo_error="INVENTARIO_NO_ENCONTRADO"
        )


class StockInsuficiente(ExcepcionDominio):
    """Se lanza cuando no hay stock suficiente para una operación"""
    def __init__(self, producto_id: int, stock_disponible: int, stock_requerido: int):
        super().__init__(
            mensaje=(
                f"Stock insuficiente para el producto {producto_id}. "
                f"Disponible: {stock_disponible}, Requerido: {stock_requerido}"
            ),
            codigo_error="STOCK_INSUFICIENTE"
        )


class StockMaximoExcedido(ExcepcionDominio):
    """Se lanza cuando una operación excedería el stock máximo"""
    def __init__(self, producto_id: int, stock_actual: int, cantidad_entrada: int, stock_maximo: int):
        super().__init__(
            mensaje=(
                f"La entrada de {cantidad_entrada} unidades excedería el stock máximo "
                f"del producto {producto_id}. Stock actual: {stock_actual}, "
                f"Máximo permitido: {stock_maximo}"
            ),
            codigo_error="STOCK_MAXIMO_EXCEDIDO"
        )


class StockNegativo(ExcepcionDominio):
    """Se lanza cuando se intenta establecer un stock negativo"""
    def __init__(self, producto_id: int, stock_intentado: int):
        super().__init__(
            mensaje=f"El stock del producto {producto_id} no puede ser negativo (intentado: {stock_intentado})",
            codigo_error="STOCK_NEGATIVO"
        )


class LimitesStockInvalidos(ExcepcionDominio):
    """Se lanza cuando los límites de stock son inválidos"""
    def __init__(self, stock_minimo: int, stock_maximo: int):
        super().__init__(
            mensaje=(
                f"Límites de stock inválidos. "
                f"El stock mínimo ({stock_minimo}) debe ser menor que el máximo ({stock_maximo})"
            ),
            codigo_error="LIMITES_STOCK_INVALIDOS"
        )


# === EXCEPCIONES DE MOVIMIENTO ===

class TipoMovimientoInvalido(ExcepcionDominio):
    """Se lanza cuando se intenta crear un movimiento con tipo inválido"""
    def __init__(self, tipo: str):
        super().__init__(
            mensaje=f"Tipo de movimiento inválido: {tipo}",
            codigo_error="TIPO_MOVIMIENTO_INVALIDO"
        )


class CantidadMovimientoInvalida(ExcepcionDominio):
    """Se lanza cuando la cantidad de un movimiento es inválida"""
    def __init__(self, cantidad: int, razon: str = ""):
        mensaje = f"Cantidad de movimiento inválida: {cantidad}"
        if razon:
            mensaje += f". {razon}"
        super().__init__(mensaje=mensaje, codigo_error="CANTIDAD_MOVIMIENTO_INVALIDA")


class MovimientoNoPermitido(ExcepcionDominio):
    """Se lanza cuando un movimiento no está permitido por reglas de negocio"""
    def __init__(self, razon: str):
        super().__init__(
            mensaje=f"Movimiento no permitido: {razon}",
            codigo_error="MOVIMIENTO_NO_PERMITIDO"
        )


# === EXCEPCIONES DE EMPRESA ===

class EmpresaNoEncontrada(ExcepcionDominio):
    """Se lanza cuando una empresa no existe"""
    def __init__(self, empresa_id: int):
        super().__init__(
            mensaje=f"La empresa con ID {empresa_id} no fue encontrada",
            codigo_error="EMPRESA_NO_ENCONTRADA"
        )


class EmpresaInactiva(ExcepcionDominio):
    """Se lanza cuando se intenta operar con una empresa inactiva"""
    def __init__(self, empresa_id: int):
        super().__init__(
            mensaje=f"La empresa con ID {empresa_id} está inactiva",
            codigo_error="EMPRESA_INACTIVA"
        )


class NITDuplicado(ExcepcionDominio):
    """Se lanza cuando se intenta crear una empresa con NIT duplicado"""
    def __init__(self, nit: str):
        super().__init__(
            mensaje=f"Ya existe una empresa con el NIT {nit}",
            codigo_error="NIT_DUPLICADO"
        )


class NITInvalido(ExcepcionDominio):
    """Se lanza cuando el formato del NIT es inválido"""
    def __init__(self, nit: str, razon: str = ""):
        mensaje = f"NIT inválido: {nit}"
        if razon:
            mensaje += f". {razon}"
        super().__init__(mensaje=mensaje, codigo_error="NIT_INVALIDO")


# === EXCEPCIONES DE USUARIO ===

class UsuarioNoEncontrado(ExcepcionDominio):
    """Se lanza cuando un usuario no existe"""
    def __init__(self, usuario_id: int):
        super().__init__(
            mensaje=f"El usuario con ID {usuario_id} no fue encontrado",
            codigo_error="USUARIO_NO_ENCONTRADO"
        )


class UsuarioSinPermisos(ExcepcionDominio):
    """Se lanza cuando un usuario no tiene permisos para una operación"""
    def __init__(self, usuario_id: int, operacion: str):
        super().__init__(
            mensaje=f"El usuario {usuario_id} no tiene permisos para: {operacion}",
            codigo_error="USUARIO_SIN_PERMISOS"
        )


class CredencialesInvalidas(ExcepcionDominio):
    """Se lanza cuando las credenciales de autenticación son inválidas"""
    def __init__(self):
        super().__init__(
            mensaje="Las credenciales proporcionadas son inválidas",
            codigo_error="CREDENCIALES_INVALIDAS"
        )


# === EXCEPCIONES DE VALIDACIÓN ===

class DatosInvalidos(ExcepcionDominio):
    """Se lanza cuando los datos proporcionados no cumplen las reglas de validación"""
    def __init__(self, campo: str, razon: str):
        super().__init__(
            mensaje=f"Datos inválidos en el campo '{campo}': {razon}",
            codigo_error="DATOS_INVALIDOS"
        )


class CampoObligatorio(ExcepcionDominio):
    """Se lanza cuando falta un campo obligatorio"""
    def __init__(self, campo: str):
        super().__init__(
            mensaje=f"El campo '{campo}' es obligatorio",
            codigo_error="CAMPO_OBLIGATORIO"
        )


class FormatoInvalido(ExcepcionDominio):
    """Se lanza cuando el formato de un dato es inválido"""
    def __init__(self, campo: str, formato_esperado: str):
        super().__init__(
            mensaje=f"Formato inválido en '{campo}'. Se esperaba: {formato_esperado}",
            codigo_error="FORMATO_INVALIDO"
        )
