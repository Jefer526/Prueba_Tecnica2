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

print(f"✅ Nombre: {producto.nombre}")
print(f"✅ Precio USD: ${producto.precio_usd}")
print(f"✅ Precio COP: ${producto.precio_cop}")

