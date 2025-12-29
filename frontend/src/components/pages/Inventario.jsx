import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../../stores/useAuthStore';
import inventarioService from '../../services/inventarioService';
import empresasService from '../../services/empresasService';
import Card from '../atoms/Card';
import Boton from '../atoms/Boton';
import Badge from '../atoms/Badge';
import DataTable from '../organisms/DataTable';
import Modal from '../molecules/Modal';
import FormField from '../molecules/FormField';
import Alert from '../atoms/Alert';
import Select from '../atoms/Select';

const Inventario = () => {
  const { esAdministrador } = useAuthStore();
  const navigate = useNavigate();
  const [registros, setRegistros] = useState([]);
  const [registrosFiltrados, setRegistrosFiltrados] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [estaCargando, setEstaCargando] = useState(true);
  const [alerta, setAlerta] = useState(null);

  // Estados para búsqueda y filtros
  const [busqueda, setBusqueda] = useState('');
  const [filtroEmpresa, setFiltroEmpresa] = useState('');
  const [filtroReorden, setFiltroReorden] = useState('todos');

  // Estados para modal de movimiento
  const [modalMovimientoAbierto, setModalMovimientoAbierto] = useState(false);
  const [productoSeleccionado, setProductoSeleccionado] = useState(null);
  const [formularioMovimiento, setFormularioMovimiento] = useState({
    producto_id: '',
    tipo_movimiento: 'ENTRADA',
    cantidad: '',
    observaciones: '',
  });

  // Estados para envío de email
  const [modalEmailAbierto, setModalEmailAbierto] = useState(false);
  const [correoDestino, setCorreoDestino] = useState('');
  const [enviandoEmail, setEnviandoEmail] = useState(false);

  const esAdmin = esAdministrador();

  // ✅ Columnas con nombres de campos CORRECTOS
  const columnas = [
    { 
      titulo: 'Producto', 
      campo: 'producto',
      renderizar: (fila) => (
        <button
          onClick={() => navigate(`/inventario/producto/${fila.id}`)}
          className="text-primary-600 hover:text-primary-700 hover:underline font-semibold"
        >
          {fila.producto_detalle?.nombre || 'N/A'}
        </button>
      )
    },
    { 
      titulo: 'Empresa', 
      campo: 'empresa',
      renderizar: (fila) => fila.empresa_detalle?.nombre || 'N/A'
    },
    { 
      titulo: 'Stock Actual',
      campo: 'stock_actual',
      renderizar: (fila) => (
        <span className={fila.requiere_reorden ? 'text-red-600 font-bold' : ''}>
          {fila.stock_actual}
        </span>
      )
    },
    { 
      titulo: 'Stock Mínimo',
      campo: 'stock_minimo'
    },
    {
      titulo: 'Requiere Reorden',
      campo: 'requiere_reorden',
      renderizar: (fila) => (
        <Badge variante={fila.requiere_reorden ? 'danger' : 'success'}>
          {fila.requiere_reorden ? 'SÍ' : 'NO'}
        </Badge>
      ),
    },
  ];

  useEffect(() => {
    cargarInventario();
    cargarEmpresas();
  }, []);

  useEffect(() => {
    filtrarRegistros();
  }, [registros, busqueda, filtroEmpresa, filtroReorden]);

  const filtrarRegistros = () => {
    let resultados = [...registros];

    if (busqueda.trim() !== '') {
      const busquedaLower = busqueda.toLowerCase();
      resultados = resultados.filter(registro => {
        const nombreProducto = (registro.producto_detalle?.nombre || '').toLowerCase();
        const codigoProducto = (registro.producto_detalle?.codigo || '').toLowerCase();
        
        return nombreProducto.includes(busquedaLower) ||
               codigoProducto.includes(busquedaLower);
      });
    }

    if (filtroEmpresa !== '') {
      resultados = resultados.filter(registro => registro.empresa === parseInt(filtroEmpresa));
    }

    if (filtroReorden === 'si') {
      resultados = resultados.filter(registro => registro.requiere_reorden);
    } else if (filtroReorden === 'no') {
      resultados = resultados.filter(registro => !registro.requiere_reorden);
    }

    setRegistrosFiltrados(resultados);
  };

  const cargarInventario = async () => {
    try {
      setEstaCargando(true);
      const datos = await inventarioService.obtenerRegistros();
      
      const registrosArray = Array.isArray(datos) ? datos : (datos.results || datos.data || []);
      
      setRegistros(registrosArray);
      setRegistrosFiltrados(registrosArray);
    } catch (error) {
      console.error('Error al cargar inventario:', error);
      mostrarAlerta('error', 'Error al cargar inventario');
    } finally {
      setEstaCargando(false);
    }
  };

  const cargarEmpresas = async () => {
    try {
      const datos = await empresasService.obtenerTodas();
      const empresasArray = Array.isArray(datos) ? datos : (datos.results || datos.data || []);
      
      const empresasActivas = empresasArray.filter(emp => emp.activo);
      setEmpresas(empresasActivas);
    } catch (error) {
      console.error('Error al cargar empresas:', error);
    }
  };

  const mostrarAlerta = (tipo, mensaje) => {
    setAlerta({ tipo, mensaje });
    setTimeout(() => setAlerta(null), 5000);
  };

  // ⭐ FUNCIÓN: Abrir modal de movimiento
  const abrirModalMovimiento = () => {
    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para registrar movimientos');
      return;
    }

    setFormularioMovimiento({
      producto_id: '',
      tipo_movimiento: 'ENTRADA',
      cantidad: '',
      observaciones: '',
    });
    setProductoSeleccionado(null);
    setModalMovimientoAbierto(true);
  };

  const cerrarModalMovimiento = () => {
    setModalMovimientoAbierto(false);
    setFormularioMovimiento({
      producto_id: '',
      tipo_movimiento: 'ENTRADA',
      cantidad: '',
      observaciones: '',
    });
    setProductoSeleccionado(null);
  };

  const manejarCambioMovimiento = (e) => {
    const { name, value } = e.target;
    
    setFormularioMovimiento((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Si cambia el producto, actualizar el producto seleccionado
    if (name === 'producto_id') {
      const producto = registros.find(r => r.producto === parseInt(value));
      setProductoSeleccionado(producto);
    }
  };

  // ⭐ FUNCIÓN: Registrar movimiento
  const manejarSubmitMovimiento = async (e) => {
    e.preventDefault();

    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para registrar movimientos');
      return;
    }

    try {
      await inventarioService.crearMovimiento({
        producto_id: parseInt(formularioMovimiento.producto_id),
        tipo_movimiento: formularioMovimiento.tipo_movimiento,
        cantidad: parseInt(formularioMovimiento.cantidad),
        observaciones: formularioMovimiento.observaciones,
      });
      
      mostrarAlerta('success', 'Movimiento registrado exitosamente');
      cerrarModalMovimiento();
      await cargarInventario();
    } catch (error) {
      console.error('Error al registrar movimiento:', error);
      const mensajeError = error.response?.data?.error 
        || error.response?.data?.detail 
        || 'Error al registrar movimiento';
      mostrarAlerta('error', mensajeError);
    }
  };

  // ⭐ FUNCIÓN: Generar PDF de inventario
  const generarPDF = async () => {
    try {
      console.log('Generando PDF...');
      mostrarAlerta('info', 'Generando PDF...');
      
      const respuesta = await inventarioService.generarPDF();
      
      console.log('Respuesta del servidor:', respuesta);
      
      if (respuesta.url) {
        console.log('URL del PDF:', respuesta.url);
        
        const enlace = document.createElement('a');
        enlace.href = respuesta.url;
        enlace.download = respuesta.nombre_archivo || 'inventario.pdf';
        enlace.target = '_blank';
        document.body.appendChild(enlace);
        enlace.click();
        document.body.removeChild(enlace);
        
        setTimeout(() => {
          mostrarAlerta('success', 'PDF generado y descargado exitosamente');
        }, 500);
      } else {
        console.error('No se recibió URL del PDF:', respuesta);
        mostrarAlerta('error', 'No se pudo obtener la URL del PDF');
      }
    } catch (error) {
      console.error('Error al generar PDF:', error);
      console.error('Detalles del error:', error.response?.data);
      mostrarAlerta('error', 'Error al generar PDF');
    }
  };

  // ⭐ FUNCIÓN: Generar PDF de movimientos
  const generarPDFMovimientos = async () => {
    try {
      console.log('Generando PDF de movimientos...');
      mostrarAlerta('info', 'Generando PDF de movimientos...');
      
      const respuesta = await inventarioService.generarPDFMovimientos();
      
      console.log('Respuesta del servidor:', respuesta);
      
      if (respuesta.url) {
        console.log('URL del PDF:', respuesta.url);
        
        const enlace = document.createElement('a');
        enlace.href = respuesta.url;
        enlace.download = respuesta.nombre_archivo || 'movimientos.pdf';
        enlace.target = '_blank';
        document.body.appendChild(enlace);
        enlace.click();
        document.body.removeChild(enlace);
        
        setTimeout(() => {
          mostrarAlerta('success', 'PDF de movimientos generado exitosamente');
        }, 500);
      } else {
        console.error('No se recibió URL del PDF:', respuesta);
        mostrarAlerta('error', 'No se pudo obtener la URL del PDF');
      }
    } catch (error) {
      console.error('Error al generar PDF de movimientos:', error);
      console.error('Detalles del error:', error.response?.data);
      mostrarAlerta('error', 'Error al generar PDF de movimientos');
    }
  };

  // ⭐ FUNCIÓN: Abrir modal de email
  const abrirModalEmail = () => {
    setCorreoDestino('');
    setModalEmailAbierto(true);
  };

  const cerrarModalEmail = () => {
    setModalEmailAbierto(false);
    setCorreoDestino('');
  };

  // ⭐ FUNCIÓN: Enviar PDF por email
  const enviarPDFPorEmail = async (e) => {
    e.preventDefault();

    if (!correoDestino.trim()) {
      mostrarAlerta('error', 'Por favor ingresa un correo electrónico');
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(correoDestino)) {
      mostrarAlerta('error', 'Por favor ingresa un correo electrónico válido');
      return;
    }

    try {
      setEnviandoEmail(true);
      mostrarAlerta('info', 'Generando y enviando PDF por email...');
      
      const respuesta = await inventarioService.enviarPDFEmail(correoDestino);
      
      console.log('Respuesta del servidor:', respuesta);
      
      mostrarAlerta('success', `PDF enviado exitosamente a ${correoDestino}`);
      cerrarModalEmail();
    } catch (error) {
      console.error('Error al enviar PDF por email:', error);
      const mensajeError = error.response?.data?.error || error.response?.data?.detail || 'Error al enviar el PDF por email';
      mostrarAlerta('error', mensajeError);
    } finally {
      setEnviandoEmail(false);
    }
  };

  const limpiarFiltros = () => {
    setBusqueda('');
    setFiltroEmpresa('');
    setFiltroReorden('todos');
  };

  // Calcular stock después del movimiento
  const calcularStockDespues = () => {
    if (!productoSeleccionado || !formularioMovimiento.cantidad) return null;

    const cantidad = parseInt(formularioMovimiento.cantidad);
    const stockActual = productoSeleccionado.stock_actual;

    switch (formularioMovimiento.tipo_movimiento) {
      case 'ENTRADA':
        return stockActual + cantidad;
      case 'SALIDA':
        return stockActual - cantidad;
      case 'AJUSTE':
        return cantidad;
      default:
        return null;
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Inventario</h1>
        <div className="flex gap-3">
          {/* ⭐ Botón Registrar Movimiento */}
          {esAdmin && (
            <Boton onClick={abrirModalMovimiento} variante="primary">
              📦 Registrar Movimiento
            </Boton>
          )}
          <Boton onClick={generarPDFMovimientos} variante="secondary">
            📋 Movimientos PDF
          </Boton>
          <Boton onClick={generarPDF} variante="secondary">
            📄 Inventario PDF
          </Boton>
          <Boton onClick={abrirModalEmail} variante="secondary">
            📧 Enviar Email
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

      <Card className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <label className="form-label">🔍 Buscar Producto</label>
            <input
              type="text"
              placeholder="Buscar por nombre o código..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="form-input"
            />
          </div>

          <div>
            <label className="form-label">Filtrar por Empresa</label>
            <Select
              nombre="filtroEmpresa"
              valor={filtroEmpresa}
              onChange={(e) => setFiltroEmpresa(e.target.value)}
              opciones={[
                { valor: '', etiqueta: 'Todas las empresas' },
                ...empresas.map(emp => ({
                  valor: emp.id,
                  etiqueta: emp.nombre
                }))
              ]}
            />
          </div>

          <div>
            <label className="form-label">Requiere Reorden</label>
            <Select
              nombre="filtroReorden"
              valor={filtroReorden}
              onChange={(e) => setFiltroReorden(e.target.value)}
              opciones={[
                { valor: 'todos', etiqueta: 'Todos' },
                { valor: 'si', etiqueta: '⚠️ Requiere Reorden' },
                { valor: 'no', etiqueta: '✓ Stock OK' },
              ]}
            />
          </div>
        </div>

        <div className="flex justify-between items-center mt-4 pt-4 border-t">
          <div className="text-sm text-gray-600">
            Mostrando <span className="font-bold">{registrosFiltrados.length}</span> de{' '}
            <span className="font-bold">{registros.length}</span> productos
          </div>
          {(busqueda || filtroEmpresa || filtroReorden !== 'todos') && (
            <Boton onClick={limpiarFiltros} variante="secondary" className="text-sm">
              🗑️ Limpiar Filtros
            </Boton>
          )}
        </div>
      </Card>

      <Card>
        <DataTable
          columnas={columnas}
          datos={registrosFiltrados}
          estaCargando={estaCargando}
        />
      </Card>

      {/* ⭐ MODAL: Registrar Movimiento */}
      {esAdmin && (
        <Modal
          estaAbierto={modalMovimientoAbierto}
          onCerrar={cerrarModalMovimiento}
          titulo="Registrar Movimiento de Inventario"
          tamaño="lg"
        >
          <form onSubmit={manejarSubmitMovimiento}>
            <div className="space-y-4">
              <div>
                <label className="form-label">
                  Producto <span className="text-red-500">*</span>
                </label>
                <Select
                  nombre="producto_id"
                  valor={formularioMovimiento.producto_id}
                  onChange={manejarCambioMovimiento}
                  opciones={registros.map(r => ({
                    valor: r.producto,
                    etiqueta: `${r.producto_detalle?.nombre || 'N/A'} - Stock: ${r.stock_actual}`
                  }))}
                  requerido
                />
              </div>

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

              {/* ⭐ Información del stock */}
              {productoSeleccionado && (
                <div className="bg-gray-50 p-4 rounded border border-gray-200">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm font-medium text-gray-700">Producto:</span>
                      <span className="text-sm text-gray-900">{productoSeleccionado.producto_detalle?.nombre}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm font-medium text-gray-700">Stock actual:</span>
                      <span className="text-sm font-bold text-gray-900">{productoSeleccionado.stock_actual} unidades</span>
                    </div>
                    {formularioMovimiento.cantidad && (
                      <div className="flex justify-between pt-2 border-t border-gray-300">
                        <span className="text-sm font-medium text-gray-700">Stock después del movimiento:</span>
                        <span className="text-sm font-bold text-primary-600">
                          {calcularStockDespues()} unidades
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
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

      {/* ⭐ MODAL: Enviar Email */}
      <Modal
        estaAbierto={modalEmailAbierto}
        onCerrar={cerrarModalEmail}
        titulo="Enviar PDF por Email"
        tamaño="md"
      >
        <form onSubmit={enviarPDFPorEmail}>
          <div className="space-y-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex gap-3">
                <div className="text-blue-600 text-xl">ℹ️</div>
                <div>
                  <p className="text-sm text-blue-800 font-medium">
                    Se generará y enviará el PDF del inventario actual
                  </p>
                  <p className="text-xs text-blue-600 mt-1">
                    El PDF incluirá todos los productos con su información de stock y valores.
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
                <li>• PDF adjunto con el inventario completo</li>
                <li>• Total de productos en inventario</li>
                <li>• Valor total del inventario</li>
                <li>• Fecha de generación</li>
              </ul>
            </div>
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

export default Inventario;