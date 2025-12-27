import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useAuthStore from '../../stores/useAuthStore';
import Card from '../atoms/Card';
import Boton from '../atoms/Boton';
import FormField from '../molecules/FormField';
import Alert from '../atoms/Alert';

const Registro = () => {
  const navigate = useNavigate();
  const { registro, estaCargando, error, limpiarError } = useAuthStore();

  const [formulario, setFormulario] = useState({
    correo: '',
    contrasena: '',
    confirmarContrasena: '',
    nombre_completo: '',
    tipo_usuario: 'EXTERNO', // Siempre EXTERNO por defecto
  });

  const [errores, setErrores] = useState({});

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario((prev) => ({
      ...prev,
      [name]: value,
    }));
    limpiarError();
    // Limpiar error específico del campo
    if (errores[name]) {
      setErrores((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validarFormulario = () => {
    const nuevosErrores = {};

    if (!formulario.correo) {
      nuevosErrores.correo = 'El correo es requerido';
    } else if (!/\S+@\S+\.\S+/.test(formulario.correo)) {
      nuevosErrores.correo = 'El correo no es válido';
    }

    if (!formulario.nombre_completo) {
      nuevosErrores.nombre_completo = 'El nombre completo es requerido';
    }

    if (!formulario.contrasena) {
      nuevosErrores.contrasena = 'La contraseña es requerida';
    } else if (formulario.contrasena.length < 8) {
      nuevosErrores.contrasena = 'La contraseña debe tener al menos 8 caracteres';
    }

    if (!formulario.confirmarContrasena) {
      nuevosErrores.confirmarContrasena = 'Debes confirmar la contraseña';
    } else if (formulario.contrasena !== formulario.confirmarContrasena) {
      nuevosErrores.confirmarContrasena = 'Las contraseñas no coinciden';
    }

    setErrores(nuevosErrores);
    return Object.keys(nuevosErrores).length === 0;
  };

  const manejarSubmit = async (e) => {
    e.preventDefault();

    if (!validarFormulario()) {
      return;
    }

    try {
      // Preparar datos para enviar (sin confirmarContrasena)
      const { confirmarContrasena, ...datosRegistro } = formulario;
      
      await registro(datosRegistro);
      navigate('/dashboard');
    } catch (error) {
      // El error ya está manejado en el store
      console.error('Error en registro:', error);
    }
  };

  return (
    <Card>
      <h2 className="text-2xl font-bold text-center mb-6">Crear Cuenta</h2>

      {error && (
        <Alert
          tipo="error"
          mensaje={error}
          onClose={limpiarError}
        />
      )}

      <form onSubmit={manejarSubmit}>
        <FormField
          etiqueta="Nombre Completo"
          nombre="nombre_completo"
          tipo="text"
          placeholder="Juan Pérez"
          valor={formulario.nombre_completo}
          onChange={manejarCambio}
          error={errores.nombre_completo}
          requerido
        />

        <FormField
          etiqueta="Correo Electrónico"
          nombre="correo"
          tipo="email"
          placeholder="correo@ejemplo.com"
          valor={formulario.correo}
          onChange={manejarCambio}
          error={errores.correo}
          requerido
        />

        <FormField
          etiqueta="Contraseña"
          nombre="contrasena"
          tipo="password"
          placeholder="••••••••"
          valor={formulario.contrasena}
          onChange={manejarCambio}
          error={errores.contrasena}
          requerido
        />

        <FormField
          etiqueta="Confirmar Contraseña"
          nombre="confirmarContrasena"
          tipo="password"
          placeholder="••••••••"
          valor={formulario.confirmarContrasena}
          onChange={manejarCambio}
          error={errores.confirmarContrasena}
          requerido
        />

        <div className="mb-4 text-sm text-gray-600">
          <p>La contraseña debe tener:</p>
          <ul className="list-disc list-inside ml-2">
            <li>Mínimo 8 caracteres</li>
            <li>No puede ser completamente numérica</li>
            <li>No puede ser muy común</li>
          </ul>
        </div>

        <Boton
          tipo="submit"
          completo
          estaCargando={estaCargando}
        >
          Registrarse
        </Boton>

        <div className="mt-4 text-center">
          <Link
            to="/login"
            className="text-primary-600 hover:text-primary-700 text-sm"
          >
            ¿Ya tienes cuenta? Inicia sesión aquí
          </Link>
        </div>
      </form>
    </Card>
  );
};

export default Registro;