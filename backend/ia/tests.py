from django.test import TestCase
from django.contrib.auth import get_user_model
from productos.models import Producto
from empresas.models import Empresa
from inventario.models import RegistroInventario, MovimientoInventario
from ia.models import ConversacionIA, MensajeIA
from decimal import Decimal

Usuario = get_user_model()


class ProductoModelTests(TestCase):
    """Tests para el modelo Producto"""
    
    def setUp(self):
        self.empresa = Empresa.objects.create(
            nit='900999888',
            nombre='Empresa Test',
            direccion='Calle 456',
            telefono='3009876543'
        )
    
    def test_crear_producto(self):
        """Test: Crear producto correctamente"""
        producto = Producto.objects.create(
            codigo='TEST001',
            nombre='Producto Test',
            caracteristicas='Test',
            precio_usd=Decimal('100.00'),
            empresa=self.empresa
        )
        
        self.assertEqual(producto.codigo, 'TEST001')
        self.assertEqual(producto.nombre, 'Producto Test')
        self.assertTrue(producto.activo)
        self.assertEqual(producto.empresa, self.empresa)
    
    def test_producto_calcula_precios(self):
        """Test: El producto calcula precios automáticamente"""
        producto = Producto.objects.create(
            codigo='TEST002',
            nombre='Monitor',
            precio_usd=Decimal('200.00'),
            empresa=self.empresa
        )
        
        self.assertIsNotNone(producto.precio_cop)
        self.assertIsNotNone(producto.precio_eur)
        self.assertGreater(producto.precio_cop, 0)
        self.assertGreater(producto.precio_eur, 0)


class InventarioModelTests(TestCase):
    """Tests para modelos de inventario"""
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            correo='inv@test.com',
            contrasena='test123',
            nombre_completo='Inv User',
            tipo_usuario='ADMINISTRADOR'
        )
        
        self.empresa = Empresa.objects.create(
            nit='900555666',
            nombre='Empresa Inventario',
            direccion='Calle 789',
            telefono='3001112233'
        )
        
        self.producto = Producto.objects.create(
            codigo='INV001',
            nombre='Producto Inventario',
            precio_usd=Decimal('50.00'),
            empresa=self.empresa
        )
    
    def test_crear_registro_inventario(self):
        """Test: Crear registro de inventario"""
        inventario = RegistroInventario.objects.create(
            producto=self.producto,
            empresa=self.empresa,
            cantidad=100,
            cantidad_minima=20
        )
        
        self.assertEqual(inventario.cantidad, 100)
        self.assertEqual(inventario.cantidad_minima, 20)
        self.assertFalse(inventario.requiere_reorden)
        self.assertTrue(inventario.activo)
    
    def test_inventario_requiere_reorden(self):
        """Test: Detectar cuando inventario requiere reorden"""
        inventario = RegistroInventario.objects.create(
            producto=self.producto,
            empresa=self.empresa,
            cantidad=5,
            cantidad_minima=10
        )
        
        self.assertTrue(inventario.requiere_reorden)
    
    def test_valor_total_inventario(self):
        """Test: Calcular valor total del inventario"""
        inventario = RegistroInventario.objects.create(
            producto=self.producto,
            empresa=self.empresa,
            cantidad=10,
            cantidad_minima=5
        )
        
        valor_esperado = 10 * self.producto.precio_usd
        self.assertEqual(inventario.valor_total, valor_esperado)
    
    def test_crear_movimiento_inventario(self):
        """Test: Crear movimiento de inventario"""
        inventario = RegistroInventario.objects.create(
            producto=self.producto,
            empresa=self.empresa,
            cantidad=50
        )
        
        movimiento = MovimientoInventario.objects.create(
            registro_inventario=inventario,
            tipo_movimiento='ENTRADA',
            cantidad=20,
            motivo='Compra de mercancía',
            usuario=self.usuario
        )
        
        self.assertEqual(movimiento.tipo_movimiento, 'ENTRADA')
        self.assertEqual(movimiento.cantidad, 20)
        self.assertEqual(movimiento.usuario, self.usuario)


class UsuarioModelTests(TestCase):
    """Tests para el modelo Usuario"""
    
    def test_crear_usuario_externo(self):
        """Test: Crear usuario externo"""
        usuario = Usuario.objects.create_user(
            correo='externo@test.com',
            contrasena='pass123',
            nombre_completo='Usuario Externo',
            tipo_usuario='EXTERNO'
        )
        
        self.assertEqual(usuario.correo, 'externo@test.com')
        self.assertEqual(usuario.tipo_usuario, 'EXTERNO')
        self.assertFalse(usuario.es_administrador)
        self.assertTrue(usuario.esta_activo)
    
    def test_crear_usuario_administrador(self):
        """Test: Crear usuario administrador"""
        usuario = Usuario.objects.create_user(
            correo='admin@test.com',
            contrasena='admin123',
            nombre_completo='Usuario Admin',
            tipo_usuario='ADMINISTRADOR',
            es_administrador=True
        )
        
        self.assertEqual(usuario.tipo_usuario, 'ADMINISTRADOR')
        self.assertTrue(usuario.es_administrador)
        self.assertTrue(usuario.tiene_permiso_administrador())
    
    def test_usuario_str(self):
        """Test: Representación en string del usuario"""
        usuario = Usuario.objects.create_user(
            correo='test@example.com',
            contrasena='test123'
        )
        
        self.assertEqual(str(usuario), 'test@example.com')


class EmpresaModelTests(TestCase):
    """Tests para el modelo Empresa"""
    
    def test_crear_empresa(self):
        """Test: Crear empresa correctamente"""
        empresa = Empresa.objects.create(
            nit='900111222',
            nombre='Tech Corp',
            direccion='Avenida Principal 100',
            telefono='3201234567'
        )
        
        self.assertEqual(empresa.nit, '900111222')
        self.assertEqual(empresa.nombre, 'Tech Corp')
        self.assertTrue(empresa.activo)
    
    def test_empresa_str(self):
        """Test: Representación en string de la empresa"""
        empresa = Empresa.objects.create(
            nit='900333444',
            nombre='Mi Empresa SAS',
            direccion='Calle 50',
            telefono='3109876543'
        )
        
        empresa_str = str(empresa)
        self.assertIn('Mi Empresa SAS', empresa_str)
        self.assertIn('900333444', empresa_str)


class ConversacionIAModelTests(TestCase):
    """Tests para modelos de IA"""
    
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            correo='ia@test.com',
            contrasena='test123',
            tipo_usuario='ADMINISTRADOR'
        )
    
    def test_crear_conversacion(self):
        """Test: Crear conversación de IA"""
        conversacion = ConversacionIA.objects.create(
            usuario=self.usuario,
            titulo='Test Conversación'
        )
        
        self.assertEqual(conversacion.titulo, 'Test Conversación')
        self.assertTrue(conversacion.activo)
        self.assertEqual(conversacion.usuario, self.usuario)
    
    def test_crear_mensaje(self):
        """Test: Crear mensaje en conversación"""
        conversacion = ConversacionIA.objects.create(
            usuario=self.usuario,
            titulo='Chat Test'
        )
        
        mensaje = MensajeIA.objects.create(
            conversacion=conversacion,
            rol='user',
            contenido='Hola chatbot'
        )
        
        self.assertEqual(mensaje.rol, 'user')
        self.assertEqual(mensaje.contenido, 'Hola chatbot')
        self.assertEqual(mensaje.conversacion, conversacion)