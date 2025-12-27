import { forwardRef } from 'react';

const Input = forwardRef(({
  tipo = 'text',
  nombre,
  placeholder,
  valor,
  onChange,
  error,
  deshabilitado = false,
  requerido = false,
  className = '',
  ...props
}, ref) => {
  const clases = [
    'form-input',
    error && 'border-red-500 focus:ring-red-500',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <input
      ref={ref}
      type={tipo}
      name={nombre}
      placeholder={placeholder}
      value={valor}
      onChange={onChange}
      disabled={deshabilitado}
      required={requerido}
      className={clases}
      {...props}
    />
  );
});

Input.displayName = 'Input';

export default Input;
