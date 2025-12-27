import { Navigate } from 'react-router-dom';
import useAuthStore from '../stores/useAuthStore';

const ProtectedRoute = ({ children, requiereAdmin = false }) => {
  const { estaAutenticado, esAdministrador } = useAuthStore();

  if (!estaAutenticado) {
    return <Navigate to="/login" replace />;
  }

  if (requiereAdmin && !esAdministrador()) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

export default ProtectedRoute;
