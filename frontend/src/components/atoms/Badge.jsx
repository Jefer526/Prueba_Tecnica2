const Badge = ({ children, variante = 'primary', className = '' }) => {
  const variantes = {
    primary: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
    gray: 'bg-gray-100 text-gray-800',
  };

  const clases = [
    'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
    variantes[variante],
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return <span className={clases}>{children}</span>;
};

export default Badge;
