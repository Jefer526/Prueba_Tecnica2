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
      
      console.log('Datos recibidos del backend:', datos);
      
      // Verificar si los datos vienen en una propiedad específica
      const empresasArray = Array.isArray(datos) ? datos : (datos.results || datos.data || []);
      
      console.log('Empresas procesadas:', empresasArray);
      
      // Mostrar TODAS las empresas (activas e inactivas)
      setEmpresas(empresasArray);
      setEmpresasFiltradas(empresasArray);
    } catch (error) {
      console.error('Error completo al cargar empresas:', error);
      console.error('Error response:', error.response?.data);
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

    try {
      if (empresaSeleccionada) {
        await empresasService.actualizar(empresaSeleccionada.nit, formulario);
        mostrarAlerta('success', 'Empresa actualizada exitosamente');
      } else {
        // Asegurar que la nueva empresa se crea como activa
        const datosConEstado = {
          ...formulario,
          activo: true
        };
        const nuevaEmpresa = await empresasService.crear(datosConEstado);
        console.log('Empresa creada:', nuevaEmpresa);
        mostrarAlerta('success', 'Empresa creada exitosamente');
      }
      cerrarModal();
      await cargarEmpresas(); // Asegurar que espera a cargar
    } catch (error) {
      console.error('Error al guardar empresa:', error);
      console.error('Error response:', error.response?.data);
      mostrarAlerta('error', error.response?.data?.detail || 'Error al guardar empresa');
    }
  };

  const manejarEliminar = async (empresa) => {
    if (window.confirm(`¿Está seguro de eliminar la empresa ${empresa.nombre}?`)) {
      try {
        console.log('Intentando eliminar empresa:', empresa);
        await empresasService.eliminar(empresa.nit);
        mostrarAlerta('success', 'Empresa eliminada exitosamente');
        await cargarEmpresas();
      } catch (error) {
        console.error('Error al eliminar empresa:', error);
        console.error('Error response:', error.response?.data);
        console.error('Error status:', error.response?.status);
        
        const mensajeError = error.response?.data?.detail 
          || error.response?.data?.error
          || 'Error al eliminar empresa';
        mostrarAlerta('error', mensajeError);
      }
    }
  };

  const manejarActivar = async (empresa) => {
    try {
      console.log('Empresa a activar/desactivar:', empresa);
      
      // Llamar al endpoint de activar (toggle)
      const resultado = await empresasService.activar(empresa.nit);
      
      console.log('Resultado de activar:', resultado);
      
      const nuevoEstado = !empresa.activo; // Invertir el estado
      mostrarAlerta(
        'success', 
        `Empresa ${nuevoEstado ? 'activada' : 'desactivada'} exitosamente`
      );
      
      await cargarEmpresas();
    } catch (error) {
      console.error('Error al cambiar estado de la empresa:', error);
      console.error('Error response:', error.response?.data);
      mostrarAlerta('error', 'Error al cambiar estado de la empresa');
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
        {/* Mostrar botón a todos los usuarios */}
        <Boton onClick={() => abrirModal()}>+ Nueva Empresa</Boton>
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
          onEditar={abrirModal}
          onEliminar={manejarEliminar}
          onVer={manejarActivar}
          estaCargando={estaCargando}
        />
      </Card>

      {/* Modal para Crear/Editar */}
      <Modal
        estaAbierto={modalAbierto}
        onCerrar={cerrarModal}
        titulo={empresaSeleccionada ? 'Editar Empresa' : 'Nueva Empresa'}
        accionesFooter={
          <>
            <Boton variante="secondary" onClick={cerrarModal}>
              Cancelar
            </Boton>
            <Boton onClick={manejarSubmit}>
              {empresaSeleccionada ? 'Actualizar' : 'Crear'}
            </Boton>
          </>
        }
      >
        <form onSubmit={manejarSubmit}>
          <FormField
            etiqueta="NIT"
            nombre="nit"
            placeholder="900123456-7"
            valor={formulario.nit}
            onChange={manejarCambio}
            deshabilitado={!!empresaSeleccionada}
            requerido
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
            placeholder="3001234567"
            valor={formulario.telefono}
            onChange={manejarCambio}
            requerido
          />
        </form>
      </Modal>
    </div>
  );
};

export default Empresas;