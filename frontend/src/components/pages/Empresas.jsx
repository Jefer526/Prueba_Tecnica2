import { useState, useEffect } from 'react';
import Boton from '../atoms/Boton';
import Card from '../atoms/Card';
import DataTable from '../organisms/DataTable';
import Modal from '../molecules/Modal';
import FormField from '../molecules/FormField';
import SearchBar from '../molecules/SearchBar';
import Alert from '../atoms/Alert';
import Badge from '../atoms/Badge';
import empresasService from '../../services/empresasService';
import useAuthStore from '../../stores/useAuthStore';

const Empresas = () => {
  const { esAdministrador } = useAuthStore();
  const [empresas, setEmpresas] = useState([]);
  const [empresasFiltradas, setEmpresasFiltradas] = useState([]);
  const [estaCargando, setEstaCargando] = useState(true);
  const [modalAbierto, setModalAbierto] = useState(false);
  const [empresaSeleccionada, setEmpresaSeleccionada] = useState(null);
  const [alerta, setAlerta] = useState(null);

  const [formulario, setFormulario] = useState({
    nit: '',
    nombre: '',
    direccion: '',
    telefono: '',
  });

  const esAdmin = esAdministrador();

  useEffect(() => {
    cargarEmpresas();
  }, []);

  const cargarEmpresas = async () => {
    try {
      setEstaCargando(true);
      const datos = await empresasService.obtenerTodas();
      
      const empresasArray = Array.isArray(datos) ? datos : (datos.results || datos.data || []);
      
      setEmpresas(empresasArray);
      setEmpresasFiltradas(empresasArray);
    } catch (error) {
      console.error('Error al cargar empresas:', error);
      mostrarAlerta('error', 'Error al cargar empresas');
    } finally {
      setEstaCargando(false);
    }
  };

  const mostrarAlerta = (tipo, mensaje) => {
    setAlerta({ tipo, mensaje });
    setTimeout(() => setAlerta(null), 5000);
  };

  const manejarBusqueda = (termino) => {
    const filtradas = empresas.filter(
      (empresa) =>
        empresa.nombre.toLowerCase().includes(termino.toLowerCase()) ||
        empresa.nit.includes(termino)
    );
    setEmpresasFiltradas(filtradas);
  };

  const abrirModal = (empresa = null) => {
    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para realizar esta acción');
      return;
    }

    if (empresa) {
      setEmpresaSeleccionada(empresa);
      setFormulario({
        nit: empresa.nit,
        nombre: empresa.nombre,
        direccion: empresa.direccion,
        telefono: empresa.telefono,
      });
    } else {
      setEmpresaSeleccionada(null);
      setFormulario({
        nit: '',
        nombre: '',
        direccion: '',
        telefono: '',
      });
    }
    setModalAbierto(true);
  };

  const cerrarModal = () => {
    setModalAbierto(false);
    setEmpresaSeleccionada(null);
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
      // ✅ Limpiar y validar datos antes de enviar
      const datosLimpios = {
        nit: formulario.nit.trim(),
        nombre: formulario.nombre.trim(),
        direccion: formulario.direccion.trim(),
        telefono: formulario.telefono.trim(),
      };

      // Validación básica en frontend
      if (!datosLimpios.nit || !datosLimpios.nombre || !datosLimpios.direccion || !datosLimpios.telefono) {
        mostrarAlerta('error', 'Todos los campos son obligatorios');
        return;
      }

      if (empresaSeleccionada) {
        await empresasService.actualizar(empresaSeleccionada.nit, datosLimpios);
        mostrarAlerta('success', 'Empresa actualizada exitosamente');
      } else {
        const datosConEstado = {
          ...datosLimpios,
          activo: true
        };
        await empresasService.crear(datosConEstado);
        mostrarAlerta('success', 'Empresa creada exitosamente');
      }
      
      cerrarModal();
      await cargarEmpresas();
    } catch (error) {
      console.error('Error al guardar empresa:', error);
      console.error('Error response:', error.response?.data);
      
      // ✅ Mejorar manejo de errores
      let mensajeError = 'Error al guardar empresa';
      
      if (error.response?.data) {
        const errores = error.response.data;
        
        // Si es un objeto con errores por campo
        if (typeof errores === 'object' && !errores.detail) {
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

  const manejarEliminar = async (empresa) => {
    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para realizar esta acción');
      return;
    }

    if (window.confirm(`¿Está seguro de eliminar la empresa ${empresa.nombre}?`)) {
      try {
        await empresasService.eliminar(empresa.nit);
        mostrarAlerta('success', 'Empresa eliminada exitosamente');
        await cargarEmpresas();
      } catch (error) {
        console.error('Error al eliminar empresa:', error);
        
        const mensajeError = error.response?.data?.detail 
          || error.response?.data?.error
          || 'Error al eliminar empresa';
        mostrarAlerta('error', mensajeError);
      }
    }
  };

  const manejarActivar = async (empresa) => {
    if (!esAdmin) {
      mostrarAlerta('error', 'No tienes permisos para realizar esta acción');
      return;
    }

    try {
      // ✅ Llamar al endpoint correcto según el estado actual
      if (empresa.activo) {
        // Si está activa → inactivar
        await empresasService.inactivar(empresa.nit);
        mostrarAlerta('success', 'Empresa inactivada exitosamente');
      } else {
        // Si está inactiva → activar
        await empresasService.activar(empresa.nit);
        mostrarAlerta('success', 'Empresa activada exitosamente');
      }
      
      await cargarEmpresas();
    } catch (error) {
      console.error('Error al cambiar estado de la empresa:', error);
      
      const mensajeError = error.response?.data?.error 
        || error.response?.data?.detail 
        || 'Error al cambiar estado de la empresa';
      
      mostrarAlerta('error', mensajeError);
    }
  };

  const columnas = [
    { titulo: 'NIT', campo: 'nit' },
    { titulo: 'Nombre', campo: 'nombre' },
    { 
      titulo: 'Dirección', 
      campo: 'direccion',
      renderizar: (fila) => fila.direccion || 'N/A'
    },
    { 
      titulo: 'Teléfono', 
      campo: 'telefono',
      renderizar: (fila) => fila.telefono || 'N/A'
    },
    {
      titulo: 'Estado',
      campo: 'activo',
      renderizar: (fila) => (
        <Badge variante={fila.activo ? 'success' : 'danger'}>
          {fila.activo ? 'Activa' : 'Inactiva'}
        </Badge>
      ),
    },
  ];

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Empresas</h1>
        {esAdmin && (
          <Boton onClick={() => abrirModal()}>+ Nueva Empresa</Boton>
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
        <div className="mb-4">
          <SearchBar
            onBuscar={manejarBusqueda}
            placeholder="Buscar por nombre o NIT..."
          />
        </div>

        <DataTable
          columnas={columnas}
          datos={empresasFiltradas}
          {...(esAdmin && { onEditar: abrirModal })}
          {...(esAdmin && { onEliminar: manejarEliminar })}
          {...(esAdmin && { onVer: manejarActivar })}
          estaCargando={estaCargando}
        />
      </Card>

      {esAdmin && (
        <Modal
          estaAbierto={modalAbierto}
          onCerrar={cerrarModal}
          titulo={empresaSeleccionada ? 'Editar Empresa' : 'Nueva Empresa'}
        >
          <form onSubmit={manejarSubmit}>
            <FormField
              etiqueta="NIT"
              nombre="nit"
              placeholder="900123456 (solo números)"
              valor={formulario.nit}
              onChange={manejarCambio}
              deshabilitado={!!empresaSeleccionada}
              requerido
              ayuda="Ingrese el NIT sin guiones ni espacios (9-10 dígitos)"
            />

            <FormField
              etiqueta="Nombre de la Empresa"
              nombre="nombre"
              placeholder="Empresa S.A.S"
              valor={formulario.nombre}
              onChange={manejarCambio}
              requerido
            />

            <FormField
              etiqueta="Dirección"
              nombre="direccion"
              placeholder="Calle 123 #45-67"
              valor={formulario.direccion}
              onChange={manejarCambio}
              requerido
            />

            <FormField
              etiqueta="Teléfono"
              nombre="telefono"
              tipo="tel"
              placeholder="3001234567 (solo números)"
              valor={formulario.telefono}
              onChange={manejarCambio}
              requerido
              ayuda="Ingrese el teléfono sin espacios ni guiones (7-15 dígitos)"
            />

            {/* ✅ CAMBIO: Botones dentro del form sin onClick, solo type */}
            <div className="flex justify-end gap-3 mt-6">
              <Boton tipo="button" variante="secondary" onClick={cerrarModal}>
                Cancelar
              </Boton>
              <Boton tipo="submit">
                {empresaSeleccionada ? 'Actualizar' : 'Crear'}
              </Boton>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
};

export default Empresas;
