const Alert = ({ tipo = 'info', titulo, mensaje, onClose, className = '' }) => {
  const tipos = {
    success: {
      bg: 'bg-green-50',
      border: 'border-green-200',
      text: 'text-green-800',
      icono: '✓',
    },
    error: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-800',
      icono: '✕',
    },
    warning: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-200',
      text: 'text-yellow-800',
      icono: '⚠',
    },
    info: {
      bg: 'bg-blue-50',
      border: 'border-blue-200',
      text: 'text-blue-800',
      icono: 'ℹ',
    },
  };

  const estilo = tipos[tipo];

  return (
    <div
      className={`${estilo.bg} ${estilo.border} ${estilo.text} border rounded-lg p-4 mb-4 ${className}`}
    >
      <div className="flex items-start">
        <span className="text-xl mr-3">{estilo.icono}</span>
        <div className="flex-1">
          {titulo && <h4 className="font-semibold mb-1">{titulo}</h4>}
          <p className="text-sm">{mensaje}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-3 text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
};

export default Alert;
