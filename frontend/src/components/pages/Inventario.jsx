import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../../stores/useAuthStore';
import inventarioService from '../../services/inventarioService';
import productosService from '../../services/productosService';
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
  const [productos, setProductos] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [estaCargando, setEstaCargando] = useState(true);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [modalMovimientoAbierto, setModalMovimientoAbierto] = useState(false);
  const [registroSeleccionado, setRegistroSeleccionado] = useState(null);
  const [alerta, setAlerta] = useState(null);

  // Estados para búsqueda y filtros
  const [busqueda, setBusqueda] = useState('');
  const [filtroEmpresa, setFiltroEmpresa] = useState('');
  const [filtroReorden, setFiltroReorden] = useState('todos');

  // Estados para envío de email
  const [modalEmailAbierto, setModalEmailAbierto] = useState(false);
  const [correoDestino, setCorreoDestino] = useState('');
  const [enviandoEmail, setEnviandoEmail] = useState(false);

  const [formulario, setFormulario] = useState({
    producto: '',
    empresa: '',
    cantidad: '',
    cantidad_minima: '10',
    ubicacion_bodega: '',
  });

  const [formularioMovimiento, setFormularioMovimiento] = useState({
    tipo_movimiento: 'ENTRADA',
    cantidad: '',
    motivo: '',
  });

  const columnas = [
    { 
      titulo: 'Producto', 
      campo: 'producto',
      renderizar: (fila) => (
        <button
          onClick={() => navigate(`/inventario/producto/${fila.producto}`)}
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
      titulo: 'Cantidad', 
      campo: 'cantidad',
      renderizar: (fila) => (
        <span className={fila.requiere_reorden ? 'text-red-600 font-bold' : ''}>
          {fila.cantidad}
        </span>
      )
    },
    { titulo: 'Cant. Mínima', campo: 'cantidad_minima' },
    { 
      titulo: 'Ubicación', 
      campo: 'ubicacion_bodega',
      renderizar: (fila) => fila.ubicacion_bodega || 'N/A'
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
    cargarProductos();
    cargarEmpresas();
  }, []);

  // Efecto para filtrar registros
  useEffect(() => {
    filtrarRegistros();
  }, [registros, busqueda, filtroEmpresa, filtroReorden]);

  const filtrarRegistros = () => {
    let resultados = [...registros];

    // Filtro por búsqueda (nombre de producto, código o ubicación)
    if (busqueda.trim() !== '') {
      const busquedaLower = busqueda.toLowerCase();
      resultados = resultados.filter(registro => {
        const nombreProducto = (registro.producto_detalle?.nombre || '').toLowerCase();
        const codigoProducto = (registro.producto || '').toLowerCase();
        const ubicacion = (registro.ubicacion_bodega || '').toLowerCase();
        
        return nombreProducto.includes(busquedaLower) ||
               codigoProducto.includes(busquedaLower) ||
               ubicacion.includes(busquedaLower);
      });
    }

    // Filtro por empresa
    if (filtroEmpresa !== '') {
      resultados = resultados.filter(registro => registro.empresa === filtroEmpresa);
    }

    // Filtro por reorden
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

  const cargarProductos = async () => {
    try {
      const datos = await productosService.obtenerTodos();
      const productosArray = Array.isArray(datos) ? datos : (datos.results || datos.data || []);
      
      const productosActivos = productosArray.filter(p => p.activo);
      setProductos(productosActivos);
    } catch (error) {
      console.error('Error al cargar productos:', error);
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

  const abrirModal = (registro = null) => {
    if (registro) {
      setRegistroSeleccionado(registro);
      setFormulario({
        producto: registro.producto,
        empresa: registro.empresa,
        cantidad: registro.cantidad,
        cantidad_minima: registro.cantidad_minima,
        ubicacion_bodega: registro.ubicacion_bodega || '',
      });
    } else {
      setRegistroSeleccionado(null);
      setFormulario({
        producto: '',
        empresa: '',
        cantidad: '',
        cantidad_minima: '10',
        ubicacion_bodega: '',
      });
    }
    setModalAbierto(true);
  };

  const cerrarModal = () => {
    setModalAbierto(false);
    setRegistroSeleccionado(null);
    setFormulario({
      producto: '',
      empresa: '',
      cantidad: '',
      cantidad_minima: '10',
      ubicacion_bodega: '',
    });
  };

  const abrirModalMovimiento = (registro) => {
    setRegistroSeleccionado(registro);
    setFormularioMovimiento({
      tipo_movimiento: 'ENTRADA',
      cantidad: '',
      motivo: '',
    });
    setModalMovimientoAbierto(true);
  };

  const cerrarModalMovimiento = () => {
    setModalMovimientoAbierto(false);
    setRegistroSeleccionado(null);
    setFormularioMovimiento({
      tipo_movimiento: 'ENTRADA',
      cantidad: '',
      motivo: '',
    });
  };

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const manejarCambioMovimiento = (e) => {
    const { name, value } = e.target;
    setFormularioMovimiento((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const manejarSubmit = async (e) => {
    e.preventDefault();

    try {
      if (registroSeleccionado) {
        await inventarioService.actualizarRegistro(registroSeleccionado.id, formulario);
        mostrarAlerta('success', 'Registro actualizado exitosamente');
      } else {
        await inventarioService.crearRegistro(formulario);
        mostrarAlerta('success', 'Registro creado exitosamente');
      }
      
      cerrarModal();
      await cargarInventario();
    } catch (error) {
      console.error('Error al guardar registro:', error);
      
      const mensajeError = error.response?.data?.detail 
        || error.response?.data?.error
        || JSON.stringify(error.response?.data)
        || 'Error al guardar registro';
      mostrarAlerta('error', mensajeError);
    }
  };

  const manejarSubmitMovimiento = async (e) => {
    e.preventDefault();

    try {
      await inventarioService.crearMovimiento({
        registro_inventario: registroSeleccionado.id,
        ...formularioMovimiento,
      });
      
      mostrarAlerta('success', 'Movimiento registrado exitosamente');
      cerrarModalMovimiento();
      await cargarInventario();
    } catch (error) {
      console.error('Error al registrar movimiento:', error);
      mostrarAlerta('error', 'Error al registrar movimiento');
    }
  };

  const generarPDF = async () => {
    try {
      console.log('Generando PDF...');
      mostrarAlerta('info', 'Generando PDF...');
      
      const respuesta = await inventarioService.generarPDF();
      
      console.log('Respuesta del servidor:', respuesta);
      
      if (respuesta.url) {
        console.log('URL del PDF:', respuesta.url);
        
        // Crear enlace temporal para descargar
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

  const generarPDFMovimientos = async () => {
    try {
      console.log('Generando PDF de movimientos...');
      mostrarAlerta('info', 'Generando PDF de movimientos...');
      
      const respuesta = await inventarioService.generarPDFMovimientos();
      
      console.log('Respuesta del servidor:', respuesta);
      
      if (respuesta.url) {
        console.log('URL del PDF:', respuesta.url);
        
        // Crear enlace temporal para descargar
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

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Inventario</h1>
        <div className="flex gap-3">
          <Boton onClick={generarPDFMovimientos} variante="secondary">
            📋 Movimientos PDF
          </Boton>
          <Boton onClick={generarPDF} variante="secondary">
            📄 Inventario PDF
          </Boton>
          <Boton onClick={abrirModalEmail} variante="secondary">
            📧 Enviar Email
          </Boton>
          <Boton onClick={() => abrirModal()}>+ Nuevo Registro</Boton>
        </div>
      </div>

      {alerta && (
        <Alert
          tipo={alerta.tipo}
          mensaje={alerta.mensaje}
          onClose={() => setAlerta(null)}
        />
      )}

      {/* Buscador y Filtros */}
      <Card className="mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Buscador */}
          <div className="md:col-span-2">
            <label className="form-label">🔍 Buscar Producto</label>
            <input
              type="text"
              placeholder="Buscar por nombre, código o ubicación..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="form-input"
            />
          </div>

          {/* Filtro por Empresa */}
          <div>
            <label className="form-label">Filtrar por Empresa</label>
            <Select
              nombre="filtroEmpresa"
              valor={filtroEmpresa}
              onChange={(e) => setFiltroEmpresa(e.target.value)}
              opciones={[
                { valor: '', etiqueta: 'Todas las empresas' },
                ...empresas.map(emp => ({
                  valor: emp.nit,
                  etiqueta: emp.nombre
                }))
              ]}
            />
          </div>

          {/* Filtro por Reorden */}
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

        {/* Botón limpiar filtros y contador de resultados */}
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
          onEditar={abrirModal}
          onVer={abrirModalMovimiento}
          accionVer="movimiento"
          estaCargando={estaCargando}
        />
      </Card>

      {/* Modal de Crear/Editar Registro */}
      <Modal
        estaAbierto={modalAbierto}
        onCerrar={cerrarModal}
        titulo={registroSeleccionado ? 'Editar Registro' : 'Nuevo Registro de Inventario'}
        tamaño="lg"
      >
        <form onSubmit={manejarSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="form-label">
                Producto <span className="text-red-500">*</span>
              </label>
              <Select
                nombre="producto"
                valor={formulario.producto}
                onChange={manejarCambio}
                opciones={productos.map(p => ({
                  valor: p.codigo,
                  etiqueta: `${p.nombre} (${p.codigo})`
                }))}
                requerido
                deshabilitado={!!registroSeleccionado}
              />
            </div>

            <div>
              <label className="form-label">
                Empresa <span className="text-red-500">*</span>
              </label>
              <Select
                nombre="empresa"
                valor={formulario.empresa}
                onChange={manejarCambio}
                opciones={empresas.map(emp => ({
                  valor: emp.nit,
                  etiqueta: emp.nombre
                }))}
                requerido
                deshabilitado={!!registroSeleccionado}
              />
            </div>

            <FormField
              etiqueta="Cantidad en Stock"
              nombre="cantidad"
              tipo="number"
              placeholder="100"
              valor={formulario.cantidad}
              onChange={manejarCambio}
              requerido
            />

            <FormField
              etiqueta="Cantidad Mínima"
              nombre="cantidad_minima"
              tipo="number"
              placeholder="10"
              valor={formulario.cantidad_minima}
              onChange={manejarCambio}
              requerido
            />

            <div className="md:col-span-2">
              <FormField
                etiqueta="Ubicación en Bodega"
                nombre="ubicacion_bodega"
                tipo="text"
                placeholder="Ej: Pasillo A, Estante 3"
                valor={formulario.ubicacion_bodega}
                onChange={manejarCambio}
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <Boton tipo="button" variante="secondary" onClick={cerrarModal}>
              Cancelar
            </Boton>
            <Boton tipo="submit">
              {registroSeleccionado ? 'Actualizar' : 'Crear'}
            </Boton>
          </div>
        </form>
      </Modal>

      {/* Modal de Movimiento */}
      <Modal
        estaAbierto={modalMovimientoAbierto}
        onCerrar={cerrarModalMovimiento}
        titulo={`Registrar Movimiento - ${registroSeleccionado?.producto_detalle?.nombre || ''}`}
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

            {registroSeleccionado && (
              <div className="bg-gray-50 p-4 rounded">
                <p className="text-sm text-gray-600">
                  <strong>Stock actual:</strong> {registroSeleccionado.cantidad} unidades
                </p>
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

      {/* Modal de Enviar Email */}
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
                    El PDF incluirá todos los productos con su información de stock, ubicación y valores.
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