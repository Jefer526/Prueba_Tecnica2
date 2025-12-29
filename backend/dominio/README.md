# Lite Thinking - Capa de Dominio

## 📋 Descripción

Paquete Python que contiene la **capa de dominio** del Sistema de Gestión de Inventario Lite Thinking, implementado siguiendo los principios de **Clean Architecture**.

Esta capa es **independiente** de frameworks, bases de datos y detalles de implementación.

## 🏗️ Arquitectura

```
dominio/
├── entidades/           # Modelos del negocio (Python puro)
│   ├── empresa.py
│   ├── producto.py
│   ├── inventario.py
│   ├── movimiento.py
│   └── usuario.py
└── excepciones/         # Excepciones de negocio
    └── excepciones_negocio.py
```

## ✨ Características

- ✅ **Sin dependencias externas** - Solo Python estándar
- ✅ **Reglas de negocio puras** - Sin Django, sin frameworks
- ✅ **Validaciones automáticas** - DataClasses con `__post_init__`
- ✅ **Enums para tipos** - Categorías, Roles, Estados
- ✅ **Excepciones específicas** - 16 excepciones del dominio

## 📦 Entidades

### Empresa
- Validación de NIT colombiano
- Validación de email y teléfono
- Estados activo/inactivo

### Producto
- Generación automática de códigos (TE0001, OF0042)
- Cálculo automático de precios en 3 monedas (USD, COP, EUR)
- Categorías predefinidas (TECNOLOGIA, OFICINA, etc.)

### RegistroInventario
- Estados de stock automáticos (CRITICO, BAJO, NORMAL, ALTO)
- Alertas de reorden
- Validación de stock mínimo/máximo

### MovimientoInventario
- Tipos: ENTRADA, SALIDA, AJUSTE, DEVOLUCION, TRASLADO
- Inmutabilidad una vez creado
- Impacto calculado según tipo

### Usuario
- Roles: ADMINISTRADOR, EXTERNO
- Hasheo de contraseñas (SHA256)
- Validación de contraseñas seguras
- Sistema de permisos

## 🚀 Instalación

### Desde el código fuente:

```bash
# Instalar en modo desarrollo (editable)
pip install -e .
```

### Desde el paquete construido:

```bash
# Construir
poetry build

# Instalar
pip install dist/lite_thinking_dominio-1.0.0-py3-none-any.whl
```

## 💻 Uso

```python
from entidades.producto import Producto, CategoriaProducto
from excepciones.excepciones_negocio import PrecioInvalido
from decimal import Decimal

# Crear un producto (ejecuta validaciones automáticas)
producto = Producto(
    nombre="Laptop HP",
    descripcion="Laptop para desarrollo",
    precio_usd=Decimal("999.99"),
    categoria=CategoriaProducto.TECNOLOGIA,
    empresa_id=1
)

# Generar código automático
producto.generar_codigo("TE", 1)  # TE0001

# Calcular precios en otras monedas
producto.calcular_precios_otras_monedas()

print(f"Código: {producto.codigo}")
print(f"Precio USD: ${producto.precio_usd}")
print(f"Precio COP: ${producto.precio_cop}")
print(f"Precio EUR: €{producto.precio_eur}")
```

## 🧪 Tests

```bash
# Ejecutar tests
poetry run pytest

# Con cobertura
poetry run pytest --cov=entidades --cov=excepciones
```

## 📐 Principios SOLID Aplicados

- **Single Responsibility**: Cada entidad tiene una única responsabilidad
- **Open/Closed**: Extensible mediante enums y herencia
- **Liskov Substitution**: Entidades intercambiables
- **Interface Segregation**: Métodos específicos por entidad
- **Dependency Inversion**: Sin dependencias de frameworks

## 🔧 Desarrollo

### Formatear código:
```bash
poetry run black entidades excepciones
```

### Verificar estilo:
```bash
poetry run flake8 entidades excepciones
```

### Type checking:
```bash
poetry run mypy entidades excepciones
```

## 📄 Licencia

Proyecto académico - Prueba Técnica Lite Thinking

## 👨‍💻 Autor

**Jeffer Niño**
- Especialista en Backend Python/Django
- Clean Architecture & SOLID Principles
