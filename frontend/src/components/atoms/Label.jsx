const Label = ({ htmlFor, children, requerido = false, className = '' }) => {
  return (
    <label htmlFor={htmlFor} className={`form-label ${className}`}>
      {children}
      {requerido && <span className="text-red-500 ml-1">*</span>}
    </label>
  );
};

export default Label;
