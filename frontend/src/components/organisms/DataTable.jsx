import { useState } from 'react';
import Boton from '../atoms/Boton';

const DataTable = ({
  columnas,
  datos = [], // ← Agregar valor por defecto
  onEditar,
  onEliminar,
  onVer,
  accionVer = 'activar', // 'activar' o 'movimiento' o 'ver'
  estaCargando = false,
  paginacion = true,
  filasPorPagina = 10,
}) => {
  const [paginaActual, setPaginaActual] = useState(1);

  // Asegurar que datos sea un array
  const datosArray = Array.isArray(datos) ? datos : [];

  const totalPaginas = Math.ceil(datosArray.length / filasPorPagina);
  const indiceInicio = (paginaActual - 1) * filasPorPagina;
  const indiceFin = indiceInicio + filasPorPagina;
  const datosPaginados = paginacion ? datosArray.slice(indiceInicio, indiceFin) : datosArray;

  const irAPagina = (numeroPagina) => {
    setPaginaActual(numeroPagina);
  };

  if (estaCargando) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (datosArray.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No hay datos para mostrar</p>
      </div>
    );
  }

  return (
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            {columnas.map((columna, index) => (
              <th key={index}>{columna.titulo}</th>
            ))}
            {(onEditar || onEliminar || onVer) && <th>Acciones</th>}
          </tr>
        </thead>
        <tbody>
          {datosPaginados.map((fila, indice) => (
            <tr key={indice}>
              {columnas.map((columna, colIndex) => (
                <td key={colIndex}>
                  {columna.renderizar
                    ? columna.renderizar(fila)
                    : fila[columna.campo]}
                </td>
              ))}
              {(onEditar || onEliminar || onVer) && (
                <td>
                  <div className="flex gap-2">
                    {onVer && (
                      <>
                        {accionVer === 'activar' ? (
                          <button
                            onClick={() => onVer(fila)}
                            className={`${fila.activo ? 'text-gray-600 hover:text-gray-800' : 'text-green-600 hover:text-green-800'}`}
                            title={fila.activo ? 'Desactivar' : 'Activar'}
                          >
                            <svg
                              className="w-5 h-5"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              {fila.activo ? (
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"
                                />
                              ) : (
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2}
                                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                                />
                              )}
                            </svg>
                          </button>
                        ) : accionVer === 'movimiento' ? (
                          <button
                            onClick={() => onVer(fila)}
                            className="text-blue-600 hover:text-blue-800"
                            title="Registrar Movimiento"
                          >
                            <svg
                              className="w-5 h-5"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
                              />
                            </svg>
                          </button>
                        ) : (
                          <button
                            onClick={() => onVer(fila)}
                            className="text-blue-600 hover:text-blue-800"
                            title="Ver detalles"
                          >
                            <svg
                              className="w-5 h-5"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                              />
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                              />
                            </svg>
                          </button>
                        )}
                      </>
                    )}
                    {onEditar && (
                      <button
                        onClick={() => onEditar(fila)}
                        className="text-yellow-600 hover:text-yellow-800"
                        title="Editar"
                      >
                        <svg
                          className="w-5 h-5"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                          />
                        </svg>
                      </button>
                    )}
                    {onEliminar && (
                      <button
                        onClick={() => onEliminar(fila)}
                        className="text-red-600 hover:text-red-800"
                        title="Eliminar"
                      >
                        <svg
                          className="w-5 h-5"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                          />
                        </svg>
                      </button>
                    )}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>

      {/* Paginación */}
      {paginacion && totalPaginas > 1 && (
        <div className="flex justify-between items-center px-6 py-3 bg-gray-50 border-t border-gray-200">
          <div className="text-sm text-gray-700">
            Mostrando {indiceInicio + 1} a {Math.min(indiceFin, datosArray.length)} de{' '}
            {datosArray.length} registros
          </div>
          <div className="flex gap-2">
            <Boton
              onClick={() => irAPagina(paginaActual - 1)}
              deshabilitado={paginaActual === 1}
              variante="secondary"
              tamano="sm"
            >
              Anterior
            </Boton>
            <div className="flex gap-1">
              {Array.from({ length: totalPaginas }, (_, i) => i + 1).map((num) => (
                <button
                  key={num}
                  onClick={() => irAPagina(num)}
                  className={`px-3 py-1 rounded ${
                    paginaActual === num
                      ? 'bg-primary-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {num}
                </button>
              ))}
            </div>
            <Boton
              onClick={() => irAPagina(paginaActual + 1)}
              deshabilitado={paginaActual === totalPaginas}
              variante="secondary"
              tamano="sm"
            >
              Siguiente
            </Boton>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataTable;