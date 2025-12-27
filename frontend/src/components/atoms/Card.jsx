const Card = ({ children, titulo, className = '', ...props }) => {
  return (
    <div className={`card ${className}`} {...props}>
      {titulo && (
        <h3 className="text-lg font-semibold text-gray-800 mb-4">{titulo}</h3>
      )}
      {children}
    </div>
  );
};

export default Card;
