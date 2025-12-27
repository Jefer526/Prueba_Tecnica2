const Boton = ({
  children,
  tipo = 'button',
  variante = 'primary',
  tamano = 'md',
  completo = false,
  deshabilitado = false,
  estaCargando = false,
  onClick,
  className = '',
  ...props
}) => {
  const variantes = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    danger: 'btn-danger',
    success: 'btn-success',
  };

  const tamanos = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
  };

  const clases = [
    'btn',
    variantes[variante],
    tamanos[tamano],
    completo && 'w-full',
    deshabilitado && 'opacity-50 cursor-not-allowed',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      type={tipo}
      onClick={onClick}
      disabled={deshabilitado || estaCargando}
      className={clases}
      {...props}
    >
      {estaCargando ? (
        <div className="flex items-center justify-center gap-2">
          <svg
            className="animate-spin h-5 w-5"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <span>Cargando...</span>
        </div>
      ) : (
        children
      )}
    </button>
  );
};

export default Boton;
