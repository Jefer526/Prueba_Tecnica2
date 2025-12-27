import Label from '../atoms/Label';
import Input from '../atoms/Input';

const FormField = ({
  etiqueta,
  nombre,
  tipo = 'text',
  placeholder,
  valor,
  onChange,
  error,
  requerido = false,
  deshabilitado = false,
  className = '',
  ...props
}) => {
  return (
    <div className={`mb-4 ${className}`}>
      {etiqueta && (
        <Label htmlFor={nombre} requerido={requerido}>
          {etiqueta}
        </Label>
      )}
      <Input
        id={nombre}
        nombre={nombre}
        tipo={tipo}
        placeholder={placeholder}
        valor={valor}
        onChange={onChange}
        error={error}
        requerido={requerido}
        deshabilitado={deshabilitado}
        {...props}
      />
      {error && <p className="form-error">{error}</p>}
    </div>
  );
};

export default FormField;
