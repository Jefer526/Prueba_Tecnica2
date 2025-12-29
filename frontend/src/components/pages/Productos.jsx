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

  const [formulario, setFormulario] = useState({
    nombre: '',
    descripcion: '',
    precio_usd: '',
    categoria: '',
    empresa_nit: '',
  });

  const esAdmin = esAdministrador();

  // ⭐ Categorías disponibles (deben coincidir con el backend)
  const categorias = [
    { valor: 'TECNOLOGIA', etiqueta: 'Tecnología' },
    { valor: 'ROPA', etiqueta: 'Ropa' },
    { valor: 'ALIMENTOS', etiqueta: 'Alimentos' },
    { valor: 'HOGAR', etiqueta: 'Hogar' },
    { valor: 'DEPORTES', etiqueta: 'Deportes' },
    { valor: 'OTROS', etiqueta: 'Otros' },
  ];

  const columnas = [
    { titulo: 'Código', campo: 'codigo' },
    { titulo: 'Nombre', campo: 'nombre' },
    { 
      titulo: 'Categoría', 
      campo: 'categoria',
      renderizar: (fila) => fila.categoria || 'N/A'
    },
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
    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para realizar esta acción');
      return;
    }

    if (producto) {
      setProductoSeleccionado(producto);
      setFormulario({
        nombre: producto.nombre,
        descripcion: producto.descripcion || '',
        precio_usd: producto.precio_usd,
        categoria: producto.categoria,
        empresa_nit: producto.empresa, // El NIT de la empresa
      });
    } else {
      setProductoSeleccionado(null);
      setFormulario({
        nombre: '',
        descripcion: '',
        precio_usd: '',
        categoria: '',
        empresa_nit: '',
      });
    }
    setModalAbierto(true);
  };

  const cerrarModal = () => {
    setModalAbierto(false);
    setProductoSeleccionado(null);
    setFormulario({
      nombre: '',
      descripcion: '',
      precio_usd: '',
      categoria: '',
      empresa_nit: '',
    });
  };

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const manejarSubmit = async (e) => {
    e.preventDefault();

    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para realizar esta acción');
      return;
    }

    try {
      // ⭐ Enviar solo los campos que el backend espera (JSON, no FormData)
      const datosProducto = {
        nombre: formulario.nombre.trim(),
        descripcion: formulario.descripcion.trim(),
        precio_usd: parseFloat(formulario.precio_usd),
        categoria: formulario.categoria,
        empresa_nit: formulario.empresa_nit,
      };

      console.log('Datos a enviar:', datosProducto);

      if (productoSeleccionado) {
        // Actualizar usa el ID del producto
        await productosService.actualizar(productoSeleccionado.id, datosProducto);
        mostrarAlerta('success', 'Producto actualizado exitosamente');
      } else {
        // Crear producto (backend genera el código automáticamente)
        await productosService.crear(datosProducto);
        mostrarAlerta('success', 'Producto creado exitosamente');
      }
      
      cerrarModal();
      await cargarProductos();
    } catch (error) {
      console.error('Error al guardar producto:', error);
      console.error('Error response:', error.response?.data);
      
      let mensajeError = 'Error al guardar producto';
      
      if (error.response?.data) {
        const errores = error.response.data;
        
        if (typeof errores === 'object' && !errores.detail && !errores.error) {
          const mensajes = Object.entries(errores).map(([campo, mensajes]) => {
            const mensajesCampo = Array.isArray(mensajes) ? mensajes.join(', ') : mensajes;
            return `${campo}: ${mensajesCampo}`;
          });
          mensajeError = mensajes.join('\n');
        } else if (errores.detail) {
          mensajeError = errores.detail;
        } else if (errores.error) {
          mensajeError = errores.error;
        }
      }
      
      mostrarAlerta('error', mensajeError);
    }
  };

  const manejarEliminar = async (producto) => {
    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para realizar esta acción');
      return;
    }

    if (window.confirm(`¿Está seguro de eliminar el producto ${producto.nombre}?`)) {
      try {
        await productosService.eliminar(producto.id);
        mostrarAlerta('success', 'Producto eliminado exitosamente');
        await cargarProductos();
      } catch (error) {
        console.error('Error al eliminar producto:', error);
        const mensajeError = error.response?.data?.error 
          || error.response?.data?.detail 
          || 'Error al eliminar producto';
        mostrarAlerta('error', mensajeError);
      }
    }
  };

  const manejarActivar = async (producto) => {
    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para realizar esta acción');
      return;
    }

    try {
      // ✅ Llamar al endpoint correcto según el estado actual
      if (producto.activo) {
        await productosService.inactivar(producto.id);
        mostrarAlerta('success', 'Producto inactivado exitosamente');
      } else {
        await productosService.activar(producto.id);
        mostrarAlerta('success', 'Producto activado exitosamente');
      }
      
      await cargarProductos();
    } catch (error) {
      console.error('Error al cambiar estado del producto:', error);
      const mensajeError = error.response?.data?.error 
        || error.response?.data?.detail 
        || 'Error al cambiar estado del producto';
      mostrarAlerta('error', mensajeError);
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Productos</h1>
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
                <label className="form-label">
                  Categoría <span className="text-red-500">*</span>
                </label>
                <Select
                  nombre="categoria"
                  valor={formulario.categoria}
                  onChange={manejarCambio}
                  opciones={categorias}
                  requerido
                />
              </div>

              <div className="md:col-span-2">
                <label className="form-label">
                  Empresa <span className="text-red-500">*</span>
                </label>
                <Select
                  nombre="empresa_nit"
                  valor={formulario.empresa_nit}
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

              <div className="md:col-span-2">
                <label className="form-label">Descripción</label>
                <Textarea
                  nombre="descripcion"
                  placeholder="Descripción y características del producto..."
                  valor={formulario.descripcion}
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