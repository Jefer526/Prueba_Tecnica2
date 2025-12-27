import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
  const { codigo } = useParams();
  const navigate = useNavigate();
  
  const [registro, setRegistro] = useState(null);
  const [movimientos, setMovimientos] = useState([]);
  const [estaCargando, setEstaCargando] = useState(true);
  const [modalMovimientoAbierto, setModalMovimientoAbierto] = useState(false);
  const [alerta, setAlerta] = useState(null);
  
  // Estados para envío de email
  const [modalEmailAbierto, setModalEmailAbierto] = useState(false);
  const [correoDestino, setCorreoDestino] = useState('');
  const [enviandoEmail, setEnviandoEmail] = useState(false);
  
  const [formularioMovimiento, setFormularioMovimiento] = useState({
    tipo_movimiento: 'ENTRADA',
    cantidad: '',
    motivo: '',
  });

  // Estadísticas
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
      titulo: 'Usuario', 
      campo: 'usuario_nombre',
      renderizar: (fila) => fila.usuario_nombre || 'N/A'
    },
    { 
      titulo: 'Motivo', 
      campo: 'motivo',
      renderizar: (fila) => fila.motivo || '-'
    },
  ];

  useEffect(() => {
    cargarDatos();
  }, [codigo]);

  const cargarDatos = async () => {
    try {
      setEstaCargando(true);
      
      // Obtener todos los registros de inventario
      const registrosData = await inventarioService.obtenerRegistros();
      const registrosArray = Array.isArray(registrosData) 
        ? registrosData 
        : (registrosData.results || registrosData.data || []);
      
      // Buscar el registro del producto específico
      const registroEncontrado = registrosArray.find(r => r.producto === codigo);
      
      if (!registroEncontrado) {
        setAlerta({ tipo: 'error', mensaje: 'Producto no encontrado en inventario' });
        return;
      }
      
      setRegistro(registroEncontrado);
      
      // Obtener movimientos del producto
      const movimientosData = await inventarioService.obtenerMovimientos({
        registro_inventario: registroEncontrado.id
      });
      
      const movimientosArray = Array.isArray(movimientosData)
        ? movimientosData
        : (movimientosData.results || movimientosData.data || []);
      
      setMovimientos(movimientosArray);
      
      // Calcular estadísticas
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
    setFormularioMovimiento({
      tipo_movimiento: 'ENTRADA',
      cantidad: '',
      motivo: '',
    });
    setModalMovimientoAbierto(true);
  };

  const cerrarModalMovimiento = () => {
    setModalMovimientoAbierto(false);
    setFormularioMovimiento({
      tipo_movimiento: 'ENTRADA',
      cantidad: '',
      motivo: '',
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

    try {
      await inventarioService.crearMovimiento({
        registro_inventario: registro.id,
        ...formularioMovimiento,
      });
      
      mostrarAlerta('success', 'Movimiento registrado exitosamente');
      cerrarModalMovimiento();
      await cargarDatos();
    } catch (error) {
      console.error('Error al registrar movimiento:', error);
      mostrarAlerta('error', 'Error al registrar movimiento');
    }
  };

  const generarPDFProducto = async () => {
    try {
      console.log('Generando PDF de movimientos del producto...');
      mostrarAlerta('info', 'Generando PDF...');
      
      const respuesta = await inventarioService.generarPDFMovimientos({
        producto_codigo: codigo
      });
      
      if (respuesta.url) {
        // Crear enlace temporal para descargar
        const enlace = document.createElement('a');
        enlace.href = respuesta.url;
        enlace.download = respuesta.nombre_archivo || `movimientos_${codigo}.pdf`;
        enlace.target = '_blank';
        document.body.appendChild(enlace);
        enlace.click();
        document.body.removeChild(enlace);
        
        setTimeout(() => {
          mostrarAlerta('success', 'PDF generado exitosamente');
        }, 500);
      }
    } catch (error) {
      console.error('Error al generar PDF:', error);
      mostrarAlerta('error', 'Error al generar PDF');
    }
  };

  const abrirModalEmail = () => {
    setCorreoDestino('');
    setModalEmailAbierto(true);
  };

  const cerrarModalEmail = () => {
    setModalEmailAbierto(false);
    setCorreoDestino('');
  };

  const enviarPDFPorEmail = async (e) => {
    e.preventDefault();

    if (!correoDestino.trim()) {
      mostrarAlerta('error', 'Por favor ingresa un correo electrónico');
      return;
    }

    // Validar formato de email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(correoDestino)) {
      mostrarAlerta('error', 'Por favor ingresa un correo electrónico válido');
      return;
    }

    try {
      setEnviandoEmail(true);
      mostrarAlerta('info', 'Generando y enviando PDF por email...');
      
      // Enviar con filtro de producto específico
      const respuesta = await inventarioService.enviarPDFMovimientosEmail(
        correoDestino,
        { producto_codigo: codigo }
      );
      
      console.log('Respuesta del servidor:', respuesta);
      
      mostrarAlerta('success', `PDF de movimientos enviado exitosamente a ${correoDestino}`);
      cerrarModalEmail();
    } catch (error) {
      console.error('Error al enviar PDF por email:', error);
      const mensajeError = error.response?.data?.error || error.response?.data?.detail || 'Error al enviar el PDF por email';
      mostrarAlerta('error', mensajeError);
    } finally {
      setEnviandoEmail(false);
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
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {registro.producto_detalle?.nombre || 'Producto'}
            </h1>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <div>
                <p className="text-sm text-gray-600">Código</p>
                <p className="font-semibold">{registro.producto}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Empresa</p>
                <p className="font-semibold">{registro.empresa_detalle?.nombre || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Stock Actual</p>
                <p className={`font-bold text-xl ${registro.requiere_reorden ? 'text-red-600' : 'text-green-600'}`}>
                  {registro.cantidad} unidades
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Stock Mínimo</p>
                <p className="font-semibold">{registro.cantidad_minima} unidades</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Ubicación</p>
                <p className="font-semibold">{registro.ubicacion_bodega || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Precio USD</p>
                <p className="font-semibold">${registro.producto_detalle?.precio_usd || 0}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Valor Total</p>
                <p className="font-bold text-xl text-primary-600">
                  ${registro.valor_total?.toLocaleString() || 0}
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
          <Boton onClick={generarPDFProducto} variante="secondary">
            📄 Descargar PDF
          </Boton>
          <Boton onClick={abrirModalEmail} variante="secondary">
            📧 Enviar Email
          </Boton>
          <Boton onClick={abrirModalMovimiento}>
            + Registrar Movimiento
          </Boton>
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
            <Boton onClick={abrirModalMovimiento} className="mt-4">
              Registrar Primer Movimiento
            </Boton>
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
                  { valor: 'AJUSTE', etiqueta: '🔧 Ajuste' },
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
            />

            <div>
              <label className="form-label">Motivo</label>
              <textarea
                name="motivo"
                placeholder="Descripción del motivo del movimiento..."
                value={formularioMovimiento.motivo}
                onChange={manejarCambioMovimiento}
                className="form-input"
                rows={3}
              />
            </div>

            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-600">
                <strong>Stock actual:</strong> {registro.cantidad} unidades
              </p>
              {formularioMovimiento.cantidad && (
                <p className="text-sm text-gray-600 mt-2">
                  <strong>Stock después del movimiento:</strong>{' '}
                  {formularioMovimiento.tipo_movimiento === 'ENTRADA' 
                    ? registro.cantidad + parseInt(formularioMovimiento.cantidad || 0)
                    : formularioMovimiento.tipo_movimiento === 'SALIDA'
                    ? registro.cantidad - parseInt(formularioMovimiento.cantidad || 0)
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

      {/* Modal de Enviar Email */}
      <Modal
        estaAbierto={modalEmailAbierto}
        onCerrar={cerrarModalEmail}
        titulo={`Enviar PDF por Email - ${registro?.producto_detalle?.nombre || ''}`}
        tamaño="md"
      >
        <form onSubmit={enviarPDFPorEmail}>
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-blue-600 text-xl">ℹ️</div>
                <div>
                  <p className="text-sm text-blue-800 font-medium">
                    Se generará y enviará el PDF con el historial de movimientos de este producto
                  </p>
                  <p className="text-xs text-blue-600 mt-1">
                    El PDF incluirá todas las entradas, salidas y ajustes del producto {registro?.producto_detalle?.nombre}.
                  </p>
                </div>
              </div>
            </div>

            <FormField
              etiqueta="Correo Electrónico de Destino"
              nombre="correo_destino"
              tipo="email"
              placeholder="ejemplo@correo.com"
              valor={correoDestino}
              onChange={(e) => setCorreoDestino(e.target.value)}
              requerido
              ayuda="Ingresa el correo electrónico donde se enviará el PDF"
            />

            <div className="bg-gray-50 p-4 rounded">
              <p className="text-sm text-gray-600 mb-2">
                <strong>El email incluirá:</strong>
              </p>
              <ul className="text-sm text-gray-600 space-y-1 ml-4">
                <li>• PDF adjunto con movimientos del producto</li>
                <li>• Total de movimientos registrados</li>
                <li>• Estadísticas de entradas, salidas y ajustes</li>
                <li>• Fecha de generación</li>
              </ul>
            </div>

            {estadisticas.totalMovimientos === 0 && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p className="text-sm text-yellow-800">
                  ⚠️ Este producto no tiene movimientos registrados aún.
                </p>
              </div>
            )}
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <Boton 
              tipo="button" 
              variante="secondary" 
              onClick={cerrarModalEmail}
              deshabilitado={enviandoEmail}
            >
              Cancelar
            </Boton>
            <Boton 
              tipo="submit"
              deshabilitado={enviandoEmail}
            >
              {enviandoEmail ? (
                <>
                  <span className="inline-block animate-spin mr-2">⏳</span>
                  Enviando...
                </>
              ) : (
                <>
                  📧 Enviar Email
                </>
              )}
            </Boton>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default DetalleProductoInventario;