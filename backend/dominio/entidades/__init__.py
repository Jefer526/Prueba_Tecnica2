# En el shell:
from dominio.entidades.producto import Producto, CategoriaProducto
from decimal import Decimal

producto = Producto(
    nombre="Test",
    descripcion="Prueba",
    precio_usd=Decimal("100"),
    categoria=CategoriaProducto.TECNOLOGIA,
    empresa_id=1
)


