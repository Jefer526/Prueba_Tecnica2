import { useState, useEffect, useRef } from 'react';
import useAuthStore from '../../stores/useAuthStore';
import chatbotService from '../../services/chatbotService';
import Card from '../atoms/Card';
import Boton from '../atoms/Boton';
import Alert from '../atoms/Alert';

const ChatbotIA = () => {
  const { usuario } = useAuthStore();
  const [conversacionId, setConversacionId] = useState(null);
  const [mensajes, setMensajes] = useState([]);
  const [mensajeActual, setMensajeActual] = useState('');
  const [enviando, setEnviando] = useState(false);
  const [alerta, setAlerta] = useState(null);
  const [sugerencias, setSugerencias] = useState([]);
  
  const mensajesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    // Mensaje de bienvenida
    setMensajes([
      {
        rol: 'assistant',
        contenido: `¡Hola ${usuario?.nombre_completo || 'Usuario'}! 👋\n\nSoy tu asistente inteligente de inventario. Puedo ayudarte con:\n\n📦 Consultar stock de productos\n⚠️ Identificar productos con stock bajo\n📊 Ver estadísticas del inventario\n🔍 Buscar productos específicos\n📈 Revisar historial de movimientos\n\n¿En qué puedo ayudarte hoy?`,
        fecha_creacion: new Date().toISOString()
      }
    ]);
    
    // Sugerencias iniciales
    setSugerencias([
      '¿Qué productos están bajos de stock?',
      'Muéstrame las estadísticas del inventario',
      'Buscar laptop'
    ]);
  }, [usuario]);

  useEffect(() => {
    // Auto-scroll al último mensaje
    mensajesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [mensajes]);

  const mostrarAlerta = (tipo, mensaje) => {
    setAlerta({ tipo, mensaje });
    setTimeout(() => setAlerta(null), 5000);
  };

  const enviarMensaje = async (e) => {
    e?.preventDefault();
    
    if (!mensajeActual.trim() || enviando) return;

    const mensajeUsuario = mensajeActual.trim();
    setMensajeActual('');
    
    // Agregar mensaje del usuario
    const nuevoMensajeUser = {
      rol: 'user',
      contenido: mensajeUsuario,
      fecha_creacion: new Date().toISOString()
    };
    setMensajes(prev => [...prev, nuevoMensajeUser]);

    setEnviando(true);

    try {
      // Enviar mensaje al backend
      const respuesta = await chatbotService.enviarMensaje(
        mensajeUsuario,
        conversacionId
      );

      // Actualizar conversación ID
      if (!conversacionId) {
        setConversacionId(respuesta.conversacion_id);
      }

      // Agregar respuesta del asistente
      const mensajeAsistente = {
        rol: 'assistant',
        contenido: respuesta.respuesta,
        fecha_creacion: new Date().toISOString(),
        acciones_ejecutadas: respuesta.acciones_ejecutadas || []
      };
      setMensajes(prev => [...prev, mensajeAsistente]);

      // Actualizar sugerencias
      if (respuesta.sugerencias && respuesta.sugerencias.length > 0) {
        setSugerencias(respuesta.sugerencias);
      }

    } catch (error) {
      console.error('Error al enviar mensaje:', error);
      mostrarAlerta('error', 'Error al enviar el mensaje. Por favor, intenta de nuevo.');
      
      // Agregar mensaje de error
      const mensajeError = {
        rol: 'assistant',
        contenido: 'Lo siento, ha ocurrido un error al procesar tu mensaje. Por favor, intenta de nuevo.',
        fecha_creacion: new Date().toISOString(),
        esError: true
      };
      setMensajes(prev => [...prev, mensajeError]);
    } finally {
      setEnviando(false);
      inputRef.current?.focus();
    }
  };

  const usarSugerencia = (sugerencia) => {
    setMensajeActual(sugerencia);
    inputRef.current?.focus();
  };

  const nuevaConversacion = () => {
    setConversacionId(null);
    setMensajes([
      {
        rol: 'assistant',
        contenido: `Nueva conversación iniciada. ¿En qué puedo ayudarte?`,
        fecha_creacion: new Date().toISOString()
      }
    ]);
    setSugerencias([
      '¿Qué productos están bajos de stock?',
      'Muéstrame las estadísticas del inventario',
      'Buscar laptop'
    ]);
  };

  const formatearMensaje = (contenido) => {
    // Convertir saltos de línea a <br>
    return contenido.split('\n').map((linea, index) => (
      <span key={index}>
        {linea}
        {index < contenido.split('\n').length - 1 && <br />}
      </span>
    ));
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <span className="text-3xl">🤖</span>
              Asistente Inteligente
            </h1>
            <p className="text-sm text-gray-600 mt-1">
              Pregúntame sobre tu inventario
            </p>
          </div>
          <Boton onClick={nuevaConversacion} variante="secondary">
            ➕ Nueva Conversación
          </Boton>
        </div>
      </div>

      {/* Alertas */}
      {alerta && (
        <div className="px-6 pt-4">
          <Alert
            tipo={alerta.tipo}
            mensaje={alerta.mensaje}
            onClose={() => setAlerta(null)}
          />
        </div>
      )}

      {/* Área de mensajes */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {mensajes.map((mensaje, index) => (
            <div
              key={index}
              className={`flex ${mensaje.rol === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  mensaje.rol === 'user'
                    ? 'bg-primary-600 text-white'
                    : mensaje.esError
                    ? 'bg-red-50 text-red-900 border border-red-200'
                    : 'bg-white border border-gray-200 text-gray-900'
                }`}
              >
                {/* Avatar */}
                <div className="flex items-start gap-3">
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-lg ${
                    mensaje.rol === 'user'
                      ? 'bg-primary-700'
                      : 'bg-gradient-to-br from-purple-500 to-blue-500'
                  }`}>
                    {mensaje.rol === 'user' ? '👤' : '🤖'}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    {/* Contenido del mensaje */}
                    <div className="text-sm leading-relaxed whitespace-pre-wrap">
                      {formatearMensaje(mensaje.contenido)}
                    </div>

                    {/* Acciones ejecutadas */}
                    {mensaje.acciones_ejecutadas && mensaje.acciones_ejecutadas.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <p className="text-xs text-gray-500">
                          🔧 Acciones: {mensaje.acciones_ejecutadas.join(', ')}
                        </p>
                      </div>
                    )}

                    {/* Timestamp */}
                    <div className={`text-xs mt-2 ${
                      mensaje.rol === 'user' ? 'text-primary-200' : 'text-gray-500'
                    }`}>
                      {new Date(mensaje.fecha_creacion).toLocaleTimeString('es-CO', {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))}

          {/* Indicador de "escribiendo..." */}
          {enviando && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-lg">
                    🤖
                  </div>
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={mensajesEndRef} />
        </div>
      </div>

      {/* Sugerencias */}
      {sugerencias.length > 0 && !enviando && (
        <div className="px-6 pb-2">
          <div className="max-w-4xl mx-auto">
            <div className="flex flex-wrap gap-2">
              {sugerencias.map((sugerencia, index) => (
                <button
                  key={index}
                  onClick={() => usarSugerencia(sugerencia)}
                  className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-full hover:bg-gray-50 hover:border-primary-500 transition-colors"
                >
                  {sugerencia}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-6 py-4">
        <div className="max-w-4xl mx-auto">
          <form onSubmit={enviarMensaje} className="flex gap-3">
            <input
              ref={inputRef}
              type="text"
              value={mensajeActual}
              onChange={(e) => setMensajeActual(e.target.value)}
              placeholder="Escribe tu mensaje..."
              disabled={enviando}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
            />
            <Boton
              tipo="submit"
              deshabilitado={!mensajeActual.trim() || enviando}
              className="px-6"
            >
              {enviando ? (
                <span className="inline-block animate-spin">⏳</span>
              ) : (
                '📤 Enviar'
              )}
            </Boton>
          </form>
          <p className="text-xs text-gray-500 mt-2 text-center">
            El asistente puede cometer errores. Verifica la información importante.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ChatbotIA;
