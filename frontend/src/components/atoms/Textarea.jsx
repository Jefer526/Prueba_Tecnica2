import { forwardRef } from 'react';

const Textarea = forwardRef(({
  nombre,
  placeholder,
  valor,
  onChange,
  filas = 4,
  error,
  deshabilitado = false,
  requerido = false,
  className = '',
  ...props
}, ref) => {
  const clases = [
    'form-input resize-none',
    error && 'border-red-500 focus:ring-red-500',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <textarea
      ref={ref}
      name={nombre}
      placeholder={placeholder}
      value={valor}
      onChange={onChange}
      rows={filas}
      disabled={deshabilitado}
      required={requerido}
      className={clases}
      {...props}
    />
  );
});

Textarea.displayName = 'Textarea';

export default Textarea;
