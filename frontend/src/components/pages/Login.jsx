import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import useAuthStore from '../../stores/useAuthStore';
import Card from '../atoms/Card';
import Boton from '../atoms/Boton';
import FormField from '../molecules/FormField';
import Alert from '../atoms/Alert';

const Login = () => {
  const navigate = useNavigate();
  const { login, estaCargando, error, limpiarError } = useAuthStore();

  const [formulario, setFormulario] = useState({
    correo: '',
    contrasena: '',
  });

  const manejarCambio = (e) => {
    const { name, value } = e.target;
    setFormulario((prev) => ({
      ...prev,
      [name]: value,
    }));
    limpiarError();
  };

  const manejarSubmit = async (e) => {
    e.preventDefault();

    try {
      await login(formulario.correo, formulario.contrasena);
      navigate('/dashboard');
    } catch (error) {
      // El error ya está manejado en el store
    }
  };

  return (
    <Card>
      <h2 className="text-2xl font-bold text-center mb-6">Iniciar Sesión</h2>

      {error && (
        <Alert
          tipo="error"
          mensaje={error}
          onClose={limpiarError}
        />
      )}

      <form onSubmit={manejarSubmit}>
        <FormField
          etiqueta="Correo Electrónico"
          nombre="correo"
          tipo="email"
          placeholder="correo@ejemplo.com"
          valor={formulario.correo}
          onChange={manejarCambio}
          requerido
        />

        <FormField
          etiqueta="Contraseña"
          nombre="contrasena"
          tipo="password"
          placeholder="••••••••"
          valor={formulario.contrasena}
          onChange={manejarCambio}
          requerido
        />

        <Boton
          tipo="submit"
          completo
          estaCargando={estaCargando}
        >
          Iniciar Sesión
        </Boton>

        <div className="mt-4 text-center">
          <Link
            to="/registro"
            className="text-primary-600 hover:text-primary-700 text-sm"
          >
            ¿No tienes cuenta? Regístrate aquí
          </Link>
        </div>
      </form>
    </Card>
  );
};

export default Login;
