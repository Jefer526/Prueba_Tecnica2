import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import useAuthStore from '../../stores/useAuthStore';
import inventarioService from '../../services/inventarioService';
import Card from '../atoms/Card';
import Boton from '../atoms/Boton';
import Badge from '../atoms/Badge';
import DataTable from '../organisms/DataTable';
import Modal from '../molecules/Modal';
import FormField from '../molecules/FormField';
import Alert from '../atoms/Alert';
import Select from '../atoms/Select';

const DetalleProductoInventario = () => {
  const { id } = useParams();  // ✅ Usar ID en lugar de codigo
  const navigate = useNavigate();
  const { esAdministrador } = useAuthStore();
  
  const [registro, setRegistro] = useState(null);
  const [movimientos, setMovimientos] = useState([]);
  const [estaCargando, setEstaCargando] = useState(true);
  const [modalMovimientoAbierto, setModalMovimientoAbierto] = useState(false);
  const [alerta, setAlerta] = useState(null);
  
  const esAdmin = esAdministrador();
  
  const [formularioMovimiento, setFormularioMovimiento] = useState({
    tipo_movimiento: 'ENTRADA',
    cantidad: '',
    observaciones: '',  // ✅ Cambio: observaciones en lugar de motivo
  });

  const [estadisticas, setEstadisticas] = useState({
    totalMovimientos: 0,
    totalEntradas: 0,
    totalSalidas: 0,
    totalAjustes: 0,
  });

  const columnas = [
    { 
      titulo: 'Fecha', 
      campo: 'fecha_movimiento',
      renderizar: (fila) => new Date(fila.fecha_movimiento).toLocaleString('es-CO')
    },
    { 
      titulo: 'Tipo', 
      campo: 'tipo_movimiento',
      renderizar: (fila) => {
        const tipos = {
          'ENTRADA': <Badge variante="success">📥 Entrada</Badge>,
          'SALIDA': <Badge variante="danger">📤 Salida</Badge>,
          'AJUSTE': <Badge variante="warning">🔧 Ajuste</Badge>,
        };
        return tipos[fila.tipo_movimiento] || fila.tipo_movimiento;
      }
    },
    { titulo: 'Cantidad', campo: 'cantidad' },
    { 
      titulo: 'Observaciones',  // ✅ Cambio: observaciones
      campo: 'observaciones',
      renderizar: (fila) => fila.observaciones || '-'
    },
  ];

  useEffect(() => {
    cargarDatos();
  }, [id]);

  const cargarDatos = async () => {
    try {
      setEstaCargando(true);
      
      // ✅ Obtener inventario directamente por ID
      const registroData = await inventarioService.obtenerPorId(id);
      
      if (!registroData) {
        setAlerta({ tipo: 'error', mensaje: 'Producto no encontrado en inventario' });
        return;
      }
      
      setRegistro(registroData);
      
      // Obtener movimientos del producto
      const movimientosData = await inventarioService.obtenerMovimientos({
        producto_id: registroData.producto
      });
      
      const movimientosArray = Array.isArray(movimientosData)
        ? movimientosData
        : (movimientosData.results || movimientosData.data || []);
      
      setMovimientos(movimientosArray);
      
      const stats = {
        totalMovimientos: movimientosArray.length,
        totalEntradas: movimientosArray.filter(m => m.tipo_movimiento === 'ENTRADA').length,
        totalSalidas: movimientosArray.filter(m => m.tipo_movimiento === 'SALIDA').length,
        totalAjustes: movimientosArray.filter(m => m.tipo_movimiento === 'AJUSTE').length,
      };
      setEstadisticas(stats);
      
    } catch (error) {
      console.error('Error al cargar datos:', error);
      setAlerta({ tipo: 'error', mensaje: 'Error al cargar los datos del producto' });
    } finally {
      setEstaCargando(false);
    }
  };

  const mostrarAlerta = (tipo, mensaje) => {
    setAlerta({ tipo, mensaje });
    setTimeout(() => setAlerta(null), 5000);
  };

  const abrirModalMovimiento = () => {
    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para registrar movimientos');
      return;
    }

    setFormularioMovimiento({
      tipo_movimiento: 'ENTRADA',
      cantidad: '',
      observaciones: '',  // ✅ Cambio
    });
    setModalMovimientoAbierto(true);
  };

  const cerrarModalMovimiento = () => {
    setModalMovimientoAbierto(false);
    setFormularioMovimiento({
      tipo_movimiento: 'ENTRADA',
      cantidad: '',
      observaciones: '',
    });
  };

  const manejarCambioMovimiento = (e) => {
    const { name, value } = e.target;
    setFormularioMovimiento((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const manejarSubmitMovimiento = async (e) => {
    e.preventDefault();

    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para registrar movimientos');
      return;
    }

    try {
      // ✅ Enviar producto_id en lugar de registro_inventario
      await inventarioService.crearMovimiento({
        producto_id: registro.producto,
        tipo_movimiento: formularioMovimiento.tipo_movimiento,
        cantidad: parseInt(formularioMovimiento.cantidad),
        observaciones: formularioMovimiento.observaciones,
      });
      
      mostrarAlerta('success', 'Movimiento registrado exitosamente');
      cerrarModalMovimiento();
      await cargarDatos();
    } catch (error) {
      console.error('Error al registrar movimiento:', error);
      const mensajeError = error.response?.data?.error 
        || error.response?.data?.detail 
        || 'Error al registrar movimiento';
      mostrarAlerta('error', mensajeError);
    }
  };

  if (estaCargando) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!registro) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Producto no encontrado</p>
        <Boton onClick={() => navigate('/inventario')} className="mt-4">
          Volver a Inventario
        </Boton>
      </div>
    );
  }

  return (
    <div>
      {/* Breadcrumb */}
      <div className="mb-4">
        <button
          onClick={() => navigate('/inventario')}
          className="text-primary-600 hover:text-primary-700 flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Volver a Inventario
        </button>
      </div>

      {/* Encabezado con info del producto */}
      <Card className="mb-6">
        <div className="flex justify-between items-start">
          <div className="w-full">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {registro.producto_detalle?.nombre || 'Producto'}
            </h1>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <div>
                <p className="text-sm text-gray-600">Código</p>
                <p className="font-semibold">{registro.producto_detalle?.codigo || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Empresa</p>
                <p className="font-semibold">{registro.empresa_detalle?.nombre || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Stock Actual</p>
                <p className={`font-bold text-xl ${registro.requiere_reorden ? 'text-red-600' : 'text-green-600'}`}>
                  {registro.stock_actual} unidades
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Stock Mínimo</p>
                <p className="font-semibold">{registro.stock_minimo} unidades</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Stock Máximo</p>
                <p className="font-semibold">{registro.stock_maximo} unidades</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Precio USD</p>
                <p className="font-semibold">${registro.producto_detalle?.precio_usd || 0}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Valor Total Inventario</p>
                <p className="font-bold text-xl text-primary-600">
                  ${((registro.producto_detalle?.precio_usd || 0) * registro.stock_actual).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Estado</p>
                {registro.requiere_reorden ? (
                  <Badge variante="danger">⚠️ Requiere Reorden</Badge>
                ) : (
                  <Badge variante="success">✓ Stock OK</Badge>
                )}
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Estadísticas de movimientos */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-1">Total Movimientos</p>
            <p className="text-3xl font-bold text-gray-900">{estadisticas.totalMovimientos}</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-1">📥 Entradas</p>
            <p className="text-3xl font-bold text-green-600">{estadisticas.totalEntradas}</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-1">📤 Salidas</p>
            <p className="text-3xl font-bold text-red-600">{estadisticas.totalSalidas}</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-gray-600 text-sm mb-1">🔧 Ajustes</p>
            <p className="text-3xl font-bold text-yellow-600">{estadisticas.totalAjustes}</p>
          </div>
        </Card>
      </div>

      {/* Acciones */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Historial de Movimientos</h2>
        <div className="flex gap-3">
          {esAdmin && (
            <Boton onClick={abrirModalMovimiento}>
              + Registrar Movimiento
            </Boton>
          )}
        </div>
      </div>

      {alerta && (
        <Alert
          tipo={alerta.tipo}
          mensaje={alerta.mensaje}
          onClose={() => setAlerta(null)}
        />
      )}

      {/* Tabla de movimientos */}
      <Card>
        {movimientos.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No hay movimientos registrados para este producto</p>
            {esAdmin && (
              <Boton onClick={abrirModalMovimiento} className="mt-4">
                Registrar Primer Movimiento
              </Boton>
            )}
          </div>
        ) : (
          <DataTable
            columnas={columnas}
            datos={movimientos}
            estaCargando={estaCargando}
            paginacion={true}
            filasPorPagina={10}
          />
        )}
      </Card>

      {/* Modal de Movimiento */}
      {esAdmin && (
        <Modal
          estaAbierto={modalMovimientoAbierto}
          onCerrar={cerrarModalMovimiento}
          titulo={`Registrar Movimiento - ${registro.producto_detalle?.nombre || ''}`}
          tamaño="md"
        >
          <form onSubmit={manejarSubmitMovimiento}>
            <div className="space-y-4">
              <div>
                <label className="form-label">
                  Tipo de Movimiento <span className="text-red-500">*</span>
                </label>
                <Select
                  nombre="tipo_movimiento"
                  valor={formularioMovimiento.tipo_movimiento}
                  onChange={manejarCambioMovimiento}
                  opciones={[
                    { valor: 'ENTRADA', etiqueta: '📥 Entrada (Aumenta stock)' },
                    { valor: 'SALIDA', etiqueta: '📤 Salida (Reduce stock)' },
                    { valor: 'AJUSTE', etiqueta: '🔧 Ajuste (Establece cantidad exacta)' },
                  ]}
                  requerido
                />
              </div>

              <FormField
                etiqueta="Cantidad"
                nombre="cantidad"
                tipo="number"
                placeholder="10"
                valor={formularioMovimiento.cantidad}
                onChange={manejarCambioMovimiento}
                requerido
                min="1"
              />

              <div>
                <label className="form-label">Observaciones</label>
                <textarea
                  name="observaciones"
                  placeholder="Descripción del motivo del movimiento..."
                  value={formularioMovimiento.observaciones}
                  onChange={manejarCambioMovimiento}
                  className="form-input"
                  rows={3}
                />
              </div>

              <div className="bg-gray-50 p-4 rounded">
                <p className="text-sm text-gray-600">
                  <strong>Stock actual:</strong> {registro.stock_actual} unidades
                </p>
                {formularioMovimiento.cantidad && (
                  <p className="text-sm text-gray-600 mt-2">
                    <strong>Stock después del movimiento:</strong>{' '}
                    {formularioMovimiento.tipo_movimiento === 'ENTRADA' 
                      ? registro.stock_actual + parseInt(formularioMovimiento.cantidad || 0)
                      : formularioMovimiento.tipo_movimiento === 'SALIDA'
                      ? registro.stock_actual - parseInt(formularioMovimiento.cantidad || 0)
                      : parseInt(formularioMovimiento.cantidad || 0)
                    } unidades
                  </p>
                )}
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Boton tipo="button" variante="secondary" onClick={cerrarModalMovimiento}>
                Cancelar
              </Boton>
              <Boton tipo="submit">
                Registrar Movimiento
              </Boton>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};

export default DetalleProductoInventario;