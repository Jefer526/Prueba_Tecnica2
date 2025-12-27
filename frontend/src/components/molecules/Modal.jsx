import { useEffect } from 'react';
import Boton from '../atoms/Boton';

const Modal = ({
  estaAbierto,
  onCerrar,
  titulo,
  children,
  tamaño = 'md',
  mostrarBotonCerrar = true,
  accionesFooter,
}) => {
  useEffect(() => {
    if (estaAbierto) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [estaAbierto]);

  if (!estaAbierto) return null;

  const tamanos = {
    sm: 'max-w-md',
    md: 'max-w-2xl',
    lg: 'max-w-4xl',
    xl: 'max-w-6xl',
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onCerrar}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div
          className={`relative bg-white rounded-lg shadow-xl ${tamanos[tamaño]} w-full animate-fadeIn`}
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h3 className="text-xl font-semibold text-gray-900">{titulo}</h3>
            {mostrarBotonCerrar && (
              <button
                onClick={onCerrar}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg
                  className="w-6 h-6"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            )}
          </div>

          {/* Body */}
          <div className="p-6">{children}</div>

          {/* Footer */}
          {accionesFooter && (
            <div className="flex justify-end gap-3 p-6 border-t border-gray-200">
              {accionesFooter}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Modal;
