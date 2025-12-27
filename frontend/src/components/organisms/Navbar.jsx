import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import useAuthStore from '../../stores/useAuthStore';
import Boton from '../atoms/Boton';

const Navbar = () => {
  const navigate = useNavigate();
  const { usuario, logout, esAdministrador } = useAuthStore();
  const [menuAbierto, setMenuAbierto] = useState(false);

  const manejarLogout = async () => {
    await logout();
    navigate('/login');
  };

  const esAdmin = esAdministrador();

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo y nombre */}
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <span className="text-2xl"></span>
              <span className="ml-2 text-xl font-bold text-primary-600">
                Lite Thinking
              </span>
            </Link>
          </div>

          {/* Menu desktop */}
          <div className="hidden md:flex items-center space-x-4">
            <Link
              to="/dashboard"
              className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Dashboard
            </Link>

            <Link
              to="/empresas"
              className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Empresas
            </Link>

            <Link
              to="/productos"
              className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Productos
            </Link>

            <Link
              to="/inventario"
              className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Inventario
            </Link>

            {/* ✅ CAMBIO: Eliminar restricción esAdmin && */}
            <Link
              to="/ia"
              className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              IA
            </Link>
            
            <Link
              to="/blockchain"
              className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium transition-colors"
            >
              Blockchain
            </Link>

            {/* Usuario */}
            <div className="flex items-center ml-4 pl-4 border-l border-gray-300">
              <span className="text-sm text-gray-700 mr-3">
                {usuario?.nombre_completo || usuario?.correo}
              </span>
              <Boton
                onClick={manejarLogout}
                variante="secondary"
                tamano="sm"
              >
                Cerrar Sesión
              </Boton>
            </div>
          </div>

          {/* Botón menú móvil */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMenuAbierto(!menuAbierto)}
              className="text-gray-700 hover:text-primary-600"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {menuAbierto ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Menu móvil */}
        {menuAbierto && (
          <div className="md:hidden pb-4">
            <Link
              to="/dashboard"
              className="block text-gray-700 hover:bg-gray-100 px-3 py-2 rounded-md"
              onClick={() => setMenuAbierto(false)}
            >
              Dashboard
            </Link>
            <Link
              to="/empresas"
              className="block text-gray-700 hover:bg-gray-100 px-3 py-2 rounded-md"
              onClick={() => setMenuAbierto(false)}
            >
              Empresas
            </Link>
            <Link
              to="/productos"
              className="block text-gray-700 hover:bg-gray-100 px-3 py-2 rounded-md"
              onClick={() => setMenuAbierto(false)}
            >
              Productos
            </Link>
            <Link
              to="/inventario"
              className="block text-gray-700 hover:bg-gray-100 px-3 py-2 rounded-md"
              onClick={() => setMenuAbierto(false)}
            >
              Inventario
            </Link>
            {/* ✅ CAMBIO: Eliminar restricción esAdmin && */}
            <Link
              to="/ia"
              className="block text-gray-700 hover:bg-gray-100 px-3 py-2 rounded-md"
              onClick={() => setMenuAbierto(false)}
            >
              IA
            </Link>
            <Link
              to="/blockchain"
              className="block text-gray-700 hover:bg-gray-100 px-3 py-2 rounded-md"
              onClick={() => setMenuAbierto(false)}
            >
              Blockchain
            </Link>
            <div className="border-t border-gray-200 mt-2 pt-2">
              <p className="text-sm text-gray-600 px-3 py-1">
                {usuario?.nombre_completo || usuario?.correo}
              </p>
              <button
                onClick={manejarLogout}
                className="block w-full text-left text-red-600 hover:bg-red-50 px-3 py-2 rounded-md"
              >
                Cerrar Sesión
              </button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
