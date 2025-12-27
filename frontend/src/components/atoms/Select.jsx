import { forwardRef } from 'react';

const Select = forwardRef(({
  nombre,
  valor,
  onChange,
  opciones = [],
  placeholder = 'Seleccione una opción',
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
    <select
      ref={ref}
      name={nombre}
      value={valor}
      onChange={onChange}
      disabled={deshabilitado}
      required={requerido}
      className={clases}
      {...props}
    >
      <option value="">{placeholder}</option>
      {opciones.map((opcion, index) => (
        <option key={index} value={opcion.valor}>
          {opcion.etiqueta}
        </option>
      ))}
    </select>
  );
});

Select.displayName = 'Select';

export default Select;
