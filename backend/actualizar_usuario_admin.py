from autenticacion.models import Usuario

# Buscar el usuario
try:
    usuario = Usuario.objects.get(correo='jefer5261@gmail.com')
    
    print(f"\n=== ANTES DE LA ACTUALIZACIÓN ===")
    print(f"Correo: {usuario.correo}")
    print(f"Tipo de Usuario: {usuario.tipo_usuario}")
    print(f"Es Administrador: {usuario.es_administrador}")
    
    # Actualizar a ADMINISTRADOR
    usuario.tipo_usuario = 'ADMINISTRADOR'
    usuario.es_administrador = True
    usuario.save()
    
    print(f"\n=== DESPUÉS DE LA ACTUALIZACIÓN ===")
    print(f"Correo: {usuario.correo}")
    print(f"Tipo de Usuario: {usuario.tipo_usuario}")
    print(f"Es Administrador: {usuario.es_administrador}")
    
    print(f"\n✅ Usuario actualizado correctamente a ADMINISTRADOR")
    print(f"\n📌 IMPORTANTE:")
    print(f"   1. Cierra sesión en la aplicación")
    print(f"   2. Vuelve a iniciar sesión")
    print(f"   3. El tipo de usuario se mostrará correctamente")
    
except Usuario.DoesNotExist:
    print(f"❌ Usuario no encontrado con correo: jefer5261@gmail.com")
except Exception as e:
    print(f"❌ Error al actualizar usuario: {e}")
