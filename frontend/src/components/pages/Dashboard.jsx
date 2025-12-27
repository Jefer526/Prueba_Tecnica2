import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../atoms/Card';
import Badge from '../atoms/Badge';
import useAuthStore from '../../stores/useAuthStore';
import autenticacionService from '../../services/autenticacionService';
import empresasService from '../../services/empresasService';
import productosService from '../../services/productosService';
import inventarioService from '../../services/inventarioService';

const Dashboard = () => {
  const navigate = useNavigate();
  const { usuario, actualizarPerfil } = useAuthStore();
  const [estadisticas, setEstadisticas] = useState({
    totalEmpresas: 0,
    totalProductos: 0,
    totalInventario: 0,
    productosBajoStock: 0,
  });
  const [estaCargando, setEstaCargando] = useState(true);

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    await Promise.all([
      cargarPerfil(),
      cargarEstadisticas()
    ]);
  };

  const cargarPerfil = async () => {
    try {
      const perfilActualizado = await autenticacionService.obtenerPerfil();
      
      // Actualizar el usuario en el store
      localStorage.setItem('usuario', JSON.stringify(perfilActualizado));
      useAuthStore.setState({ usuario: perfilActualizado });
    } catch (error) {
      console.error('Error al cargar perfil:', error);
    }
  };

  const cargarEstadisticas = async () => {
    try {
      const [empresasData, productosData, inventarioData, bajoStockData] = await Promise.all([
        empresasService.obtenerTodas(),
        productosService.obtenerTodos(),
        inventarioService.obtenerRegistros(),
        inventarioService.obtenerBajoStock(),
      ]);

      // Normalizar respuestas - pueden venir como array directo o como objeto con results/data
      const empresas = Array.isArray(empresasData) 
        ? empresasData 
        : (empresasData.results || empresasData.data || []);
      
      const productos = Array.isArray(productosData)
        ? productosData
        : (productosData.results || productosData.data || []);
      
      const inventario = Array.isArray(inventarioData)
        ? inventarioData
        : (inventarioData.results || inventarioData.data || []);

      setEstadisticas({
        totalEmpresas: empresas.length || 0,
        totalProductos: productos.length || 0,
        totalInventario: inventario.length || 0,
        productosBajoStock: bajoStockData.total || bajoStockData.registros?.length || 0,
      });
    } catch (error) {
      console.error('Error al cargar estadísticas:', error);
    } finally {
      setEstaCargando(false);
    }
  };

  if (estaCargando) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Bienvenido, {usuario?.nombre_completo || usuario?.correo}
        </p>
      </div>

      {/* Tarjetas de Estadísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Tarjeta Empresas - Clickeable */}
        <div
          onClick={() => navigate('/empresas')}
          className="cursor-pointer transform transition-all duration-200 hover:scale-105 hover:shadow-xl"
        >
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Empresas</p>
                <p className="text-3xl font-bold text-primary-600">
                  {estadisticas.totalEmpresas}
                </p>
              </div>
              <div className="text-4xl">🏢</div>
            </div>
            <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
              <span>Ver empresas</span>
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </Card>
        </div>

        {/* Tarjeta Productos - Clickeable */}
        <div
          onClick={() => navigate('/productos')}
          className="cursor-pointer transform transition-all duration-200 hover:scale-105 hover:shadow-xl"
        >
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Productos</p>
                <p className="text-3xl font-bold text-green-600">
                  {estadisticas.totalProductos}
                </p>
              </div>
              <div className="text-4xl">📦</div>
            </div>
            <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
              <span>Ver productos</span>
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </Card>
        </div>

        {/* Tarjeta Inventario - Clickeable */}
        <div
          onClick={() => navigate('/inventario')}
          className="cursor-pointer transform transition-all duration-200 hover:scale-105 hover:shadow-xl"
        >
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Registros Inventario</p>
                <p className="text-3xl font-bold text-blue-600">
                  {estadisticas.totalInventario}
                </p>
              </div>
              <div className="text-4xl">📊</div>
            </div>
            <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
              <span>Ver inventario</span>
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </Card>
        </div>

        {/* Tarjeta Bajo Stock - Clickeable */}
        <div
          onClick={() => navigate('/inventario')}
          className="cursor-pointer transform transition-all duration-200 hover:scale-105 hover:shadow-xl"
        >
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Bajo Stock</p>
                <p className="text-3xl font-bold text-red-600">
                  {estadisticas.productosBajoStock}
                </p>
              </div>
              <div className="text-4xl">⚠️</div>
            </div>
            <div className="mt-2 text-xs text-gray-500 flex items-center gap-1">
              <span>Ver productos críticos</span>
              <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </Card>
        </div>
      </div>

      {/* Información del Usuario */}
      <Card titulo="Información de la Cuenta">
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-gray-600">Correo:</span>
            <span className="font-medium">{usuario?.correo}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Tipo de Usuario:</span>
            <Badge
              variante={
                usuario?.tipo_usuario === 'ADMINISTRADOR' ? 'success' : 'gray'
              }
            >
              {usuario?.tipo_usuario}
            </Badge>
          </div>
          {usuario?.fecha_creacion && (
            <div className="flex justify-between">
              <span className="text-gray-600">Miembro desde:</span>
              <span className="font-medium">
                {new Date(usuario.fecha_creacion).toLocaleDateString('es-CO')}
              </span>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default Dashboard;