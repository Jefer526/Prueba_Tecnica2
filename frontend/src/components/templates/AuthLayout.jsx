import { Outlet } from 'react-router-dom';

const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary-600 mb-2">
            Lite Thinking
          </h1>
          <p className="text-gray-600">Sistema de Gestión de Inventario</p>
        </div>
        <Outlet />
      </div>
    </div>
  );
};

export default AuthLayout;
