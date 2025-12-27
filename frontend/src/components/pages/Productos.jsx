import { useState, useEffect } from 'react';
import useAuthStore from '../../stores/useAuthStore';
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
import Textarea from '../atoms/Textarea';


const Productos = () => {
  const { esAdministrador } = useAuthStore();
  const [productos, setProductos] = useState([]);
  const [productosFiltrados, setProductosFiltrados] = useState([]);
  const [empresas, setEmpresas] = useState([]);
  const [estaCargando, setEstaCargando] = useState(true);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [productoSeleccionado, setProductoSeleccionado] = useState(null);
  const [alerta, setAlerta] = useState(null);
  const [imagenPreview, setImagenPreview] = useState(null);

  const [formulario, setFormulario] = useState({
    codigo: '',
    nombre: '',
    caracteristicas: '',
    precio_usd: '',
    empresa: '',
    imagen: null,
  });

  // ✅ Obtener si es administrador
  const esAdmin = esAdministrador();

  const columnas = [
    { titulo: 'Código', campo: 'codigo' },
    { titulo: 'Nombre', campo: 'nombre' },
    { 
      titulo: 'USD', 
      campo: 'precio_usd',
      renderizar: (fila) => `$${parseFloat(fila.precio_usd).toFixed(2)}`
    },
    { 
      titulo: 'COP', 
      campo: 'precio_cop',
      renderizar: (fila) => `$${parseFloat(fila.precio_cop || 0).toLocaleString('es-CO', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`
    },
    { 
      titulo: 'EUR', 
      campo: 'precio_eur',
      renderizar: (fila) => `€${parseFloat(fila.precio_eur || 0).toFixed(2)}`
    },
    { 
      titulo: 'Empresa', 
      campo: 'empresa',
      renderizar: (fila) => fila.empresa_detalle?.nombre || fila.empresa_nombre || 'N/A'
    },
    {
      titulo: 'Estado',
      campo: 'activo',
      renderizar: (fila) => (
        <Badge variante={fila.activo ? 'success' : 'danger'}>
          {fila.activo ? 'Activo' : 'Inactivo'}
        </Badge>
      ),
    },
  ];

  useEffect(() => {
    cargarProductos();
    cargarEmpresas();
  }, []);

  const cargarProductos = async () => {
    try {
      setEstaCargando(true);
      const datos = await productosService.obtenerTodos();
      
      const productosArray = Array.isArray(datos) ? datos : (datos.results || datos.data || []);
      
      setProductos(productosArray);
      setProductosFiltrados(productosArray);
    } catch (error) {
      console.error('Error al cargar productos:', error);
      mostrarAlerta('error', 'Error al cargar productos');
    } finally {
      setEstaCargando(false);
    }
  };

  const cargarEmpresas = async () => {
    try {
      const datos = await empresasService.obtenerTodas();
      const empresasArray = Array.isArray(datos) ? datos : (datos.results || datos.data || []);
      
      // Filtrar solo empresas activas
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

  const abrirModal = (producto = null) => {
    // ✅ Verificar permisos antes de abrir modal
    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para realizar esta acción');
      return;
    }

    if (producto) {
      setProductoSeleccionado(producto);
      setFormulario({
        codigo: producto.codigo,
        nombre: producto.nombre,
        caracteristicas: producto.caracteristicas || '',
        precio_usd: producto.precio_usd,
        empresa: producto.empresa,
        imagen: null,
      });
      setImagenPreview(producto.imagen);
    } else {
      setProductoSeleccionado(null);
      setFormulario({
        codigo: '',
        nombre: '',
        caracteristicas: '',
        precio_usd: '',
        empresa: '',
        imagen: null,
      });
      setImagenPreview(null);
    }
    setModalAbierto(true);
  };

  const cerrarModal = () => {
    setModalAbierto(false);
    setProductoSeleccionado(null);
    setImagenPreview(null);
    setFormulario({
      codigo: '',
      nombre: '',
      caracteristicas: '',
      precio_usd: '',
      empresa: '',
      imagen: null,
    });
  };

  const generarCodigo = async (nombre) => {
    if (!nombre || nombre.length < 2) return '';
    
    // Tomar las 2 primeras letras y convertir a mayúsculas
    const prefijo = nombre.substring(0, 2).toUpperCase();
    
    // Buscar productos existentes con ese prefijo
    const productosConPrefijo = productos.filter(p => 
      p.codigo.startsWith(prefijo)
    );
    
    // Obtener el número más alto
    let numeroMasAlto = 0;
    productosConPrefijo.forEach(p => {
      const numero = parseInt(p.codigo.substring(2));
      if (!isNaN(numero) && numero > numeroMasAlto) {
        numeroMasAlto = numero;
      }
    });
    
    // Generar el siguiente número
    const siguienteNumero = (numeroMasAlto + 1).toString().padStart(3, '0');
    
    return `${prefijo}${siguienteNumero}`;
  };

  const manejarCambio = async (e) => {
    const { name, value } = e.target;
    
    setFormulario((prev) => ({
      ...prev,
      [name]: value,
    }));
    
    // Si cambia el nombre y no estamos editando, generar código automáticamente
    if (name === 'nombre' && !productoSeleccionado && value.length >= 2) {
      const codigoGenerado = await generarCodigo(value);
      setFormulario((prev) => ({
        ...prev,
        codigo: codigoGenerado,
      }));
    }
  };

  const manejarCambioImagen = (e) => {
    const archivo = e.target.files[0];
    if (archivo) {
      setFormulario((prev) => ({
        ...prev,
        imagen: archivo,
      }));
      
      // Preview de la imagen
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagenPreview(reader.result);
      };
      reader.readAsDataURL(archivo);
    }
  };

  const manejarSubmit = async (e) => {
    e.preventDefault();

    // ✅ Verificar permisos antes de guardar
    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para realizar esta acción');
      return;
    }

    try {
      // Crear FormData para enviar archivo
      const formData = new FormData();
      formData.append('codigo', formulario.codigo);
      formData.append('nombre', formulario.nombre);
      formData.append('caracteristicas', formulario.caracteristicas || '');
      formData.append('precio_usd', formulario.precio_usd);
      formData.append('empresa', formulario.empresa);
      formData.append('activo', 'true');
      
      // Solo agregar imagen si existe
      if (formulario.imagen) {
        formData.append('imagen', formulario.imagen);
      }

      // Log para debug
      console.log('Datos a enviar:');
      for (let pair of formData.entries()) {
        console.log(pair[0] + ': ' + pair[1]);
      }

      if (productoSeleccionado) {
        await productosService.actualizar(productoSeleccionado.codigo, formData);
        mostrarAlerta('success', 'Producto actualizado exitosamente');
      } else {
        await productosService.crear(formData);
        mostrarAlerta('success', 'Producto creado exitosamente');
      }
      
      cerrarModal();
      await cargarProductos();
    } catch (error) {
      console.error('Error al guardar producto:', error);
      console.error('Error response:', error.response?.data);
      
      const mensajeError = error.response?.data?.detail 
        || error.response?.data?.error
        || JSON.stringify(error.response?.data)
        || 'Error al guardar producto';
      mostrarAlerta('error', mensajeError);
    }
  };

  const manejarEliminar = async (producto) => {
    // ✅ Verificar permisos antes de eliminar
    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para realizar esta acción');
      return;
    }

    if (window.confirm(`¿Está seguro de eliminar el producto ${producto.nombre}?`)) {
      try {
        await productosService.eliminar(producto.codigo);
        mostrarAlerta('success', 'Producto eliminado exitosamente');
        await cargarProductos();
      } catch (error) {
        console.error('Error al eliminar producto:', error);
        mostrarAlerta('error', 'Error al eliminar producto');
      }
    }
  };

  const manejarActivar = async (producto) => {
    // ✅ Verificar permisos antes de activar/desactivar
    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para realizar esta acción');
      return;
    }

    try {
      await productosService.activar(producto.codigo);
      const nuevoEstado = !producto.activo;
      mostrarAlerta(
        'success', 
        `Producto ${nuevoEstado ? 'activado' : 'desactivado'} exitosamente`
      );
      await cargarProductos();
    } catch (error) {
      console.error('Error al cambiar estado del producto:', error);
      mostrarAlerta('error', 'Error al cambiar estado del producto');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Productos</h1>
        {/* ✅ Solo mostrar botón si es administrador */}
        {esAdmin && (
          <Boton onClick={() => abrirModal()}>+ Nuevo Producto</Boton>
        )}
      </div>

      {alerta && (
        <Alert
          tipo={alerta.tipo}
          mensaje={alerta.mensaje}
          onClose={() => setAlerta(null)}
        />
      )}

      <Card>
        <DataTable
          columnas={columnas}
          datos={productosFiltrados}
          onEditar={esAdmin ? abrirModal : undefined}
          onEliminar={esAdmin ? manejarEliminar : undefined}
          onVer={esAdmin ? manejarActivar : undefined}
          estaCargando={estaCargando}
        />
      </Card>

      {/* ✅ Solo renderizar modal si es administrador */}
      {esAdmin && (
        <Modal
          estaAbierto={modalAbierto}
          onCerrar={cerrarModal}
          titulo={productoSeleccionado ? 'Editar Producto' : 'Nuevo Producto'}
          tamaño="lg"
        >
          <form onSubmit={manejarSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                etiqueta="Nombre del Producto"
                nombre="nombre"
                tipo="text"
                placeholder="Ej: Laptop HP Pavilion"
                valor={formulario.nombre}
                onChange={manejarCambio}
                requerido
              />

              <div>
                <FormField
                  etiqueta="Código del Producto"
                  nombre="codigo"
                  tipo="text"
                  placeholder={productoSeleccionado ? "" : "Ej: LA001"}
                  valor={formulario.codigo}
                  onChange={manejarCambio}
                  requerido
                  deshabilitado={!!productoSeleccionado}
                />
                {!productoSeleccionado && formulario.nombre && (
                  <p className="text-xs text-gray-500 mt-1">
                    💡 Generado automáticamente. Puedes editarlo si deseas.
                  </p>
                )}
              </div>

              <div className="md:col-span-2">
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
                />
              </div>

              <FormField
                etiqueta="Precio USD"
                nombre="precio_usd"
                tipo="number"
                step="0.01"
                placeholder="99.99"
                valor={formulario.precio_usd}
                onChange={manejarCambio}
                requerido
              />

              <div>
                <label className="form-label">Imagen del Producto</label>
                <input
                  type="file"
                  name="imagen"
                  accept="image/*"
                  onChange={manejarCambioImagen}
                  className="form-input"
                />
                {imagenPreview && (
                  <img
                    src={imagenPreview}
                    alt="Preview"
                    className="mt-2 w-32 h-32 object-cover rounded"
                  />
                )}
              </div>

              <div className="md:col-span-2">
                <label className="form-label">Características</label>
                <Textarea
                  nombre="caracteristicas"
                  placeholder="Descripción y características del producto..."
                  valor={formulario.caracteristicas}
                  onChange={manejarCambio}
                  filas={4}
                />
              </div>
            </div>

            <div className="flex justify-end gap-3 mt-6">
              <Boton tipo="button" variante="secondary" onClick={cerrarModal}>
                Cancelar
              </Boton>
              <Boton tipo="submit">
                {productoSeleccionado ? 'Actualizar' : 'Crear'}
              </Boton>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};

export default Productos;
