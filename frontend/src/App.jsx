import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './routes/ProtectedRoute';
import AuthLayout from './components/templates/AuthLayout';
import MainLayout from './components/templates/MainLayout';
import Login from './components/pages/Login';
import Registro from './components/pages/Registro';
import Dashboard from './components/pages/Dashboard';
import Empresas from './components/pages/Empresas';
import Productos from './components/pages/Productos';
import Inventario from './components/pages/Inventario';
import DetalleProductoInventario from './components/pages/DetalleProductoInventario';
import useAuthStore from './stores/useAuthStore';
import ChatbotIA from './components/pages/ChatbotIA';

function App() {
  const { estaAutenticado } = useAuthStore();

  return (
    <BrowserRouter>
      <Routes>
        {/* Rutas Públicas */}
        <Route element={<AuthLayout />}>
          <Route 
            path="/login" 
            element={
              estaAutenticado ? <Navigate to="/dashboard" replace /> : <Login />
            } 
          />
          <Route 
            path="/registro" 
            element={
              estaAutenticado ? <Navigate to="/dashboard" replace /> : <Registro />
            } 
          />
        </Route>

        {/* Rutas Protegidas */}
        <Route
          element={
            <ProtectedRoute>
              <MainLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/empresas" element={<Empresas />} />
          <Route path="/productos" element={<Productos />} />
          <Route path="/inventario" element={<Inventario />} />
          <Route path="/inventario/producto/:codigo" element={<DetalleProductoInventario />} />
          <Route path="/ia" element={<ChatbotIA />} />
        </Route>

        {/* Redirección por defecto */}
        <Route 
          path="/" 
          element={
            <Navigate to={estaAutenticado ? "/dashboard" : "/login"} replace />
          } 
        />

        {/* Ruta 404 */}
        <Route 
          path="*" 
          element={
            <Navigate to={estaAutenticado ? "/dashboard" : "/login"} replace />
          } 
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
