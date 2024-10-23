from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from usuario import Usuario
import threading

class Servidor:
    def __init__(self):
        self.usuarios = []  # Lista de usuarios
        self.sesion_iniciada = False
        self.sesion = {}
        self.running = False  # Estado del servidor
        self.server = None  # Almacenará la instancia del servidor
        self.server_thread = None  # Hilo para el servidor
        self.ip_cliente = None # Almacena ultima IP
        self.comando_recibido = None # Almacena el ultimo comando recibido de un cliente

    def get_estado_servidor(self):
        return self.running

    def get_sesion(self):
        return self.sesion
    
    def get_usuarios(self):
        return self.usuarios
    
    def agregar_usuario(self, nombre_usuario, contrasena):
        # Verificamos si el usuario ya existe
        for usuario in self.usuarios:
            if nombre_usuario == usuario.nombre_usuario:
                print("El usuario ingresado ya existe, por favor, ingrese un usuario válido.")
                return  # Salimos del método si el usuario ya existe
        
        # Si el usuario no existe, agregamos el nuevo usuario
        nuevo_usuario = Usuario(nombre_usuario, contrasena)
        self.usuarios.append(nuevo_usuario)
        print(f"Usuario {nombre_usuario} agregado correctamente.")
        
        # Guardar automáticamente el nuevo usuario en el archivo CSV
        nuevo_usuario.guardar_usuarios_csv()

    def iniciar_sesion(self):
        while not self.sesion_iniciada:
            nombre_usuario = input("Ingrese el nombre de usuario (o 'salir' para cancelar): ")
            
            if nombre_usuario.lower() == "salir":
                print("Sesión cancelada.")
                return None
            
            # Inicializamos la variable para verificar si el usuario existe
            usuario_encontrado = None
            for usuario in self.usuarios:
                if usuario.nombre_usuario == nombre_usuario:
                    usuario_encontrado = usuario
                    break
            
            # Si no encontramos el usuario
            if usuario_encontrado is None:
                print("El usuario ingresado no existe, por favor, ingrese un usuario válido.")
            else:
                # Si encontramos el usuario, pedimos la contraseña
                contrasena = input("Ingrese la contraseña: ")
                if usuario_encontrado.contrasena == contrasena:
                    print(f"Bienvenido {nombre_usuario}!")
                    self.sesion_iniciada = True
                    # Devolvemos un diccionario con los datos del usuario
                    self.sesion = {'nombre_usuario': nombre_usuario, 'contrasena': contrasena}
                else:
                    print("La contraseña ingresada es incorrecta. Pruebe nuevamente.")

        return None
    
    def cerrar_sesion(self):
        self.sesion_iniciada = False
        self.sesion = {}

    def iniciar_servidor(self, host="localhost", port=8080):
        if self.sesion and 'nombre_usuario' in self.sesion:
            nombre_usuario = self.sesion['nombre_usuario']
            # Verificamos si el usuario tiene permisos de administrador
            for usuario in self.usuarios:
                if usuario.nombre_usuario == nombre_usuario and usuario.admin:
                    """Inicia el servidor XML-RPC."""
                    self.running = True  # Cambia el estado a en ejecución

                    def run_server():
                        self.server = SimpleXMLRPCServer(
                            (host, port),
                            requestHandler=self.MyRequestHandler  # Usa la clase de manejador personalizada
                        )
                        self.server.register_instance(self)
                        print(f"Servidor XML-RPC escuchando en {host}:{port}...")
                        while self.running:
                            self.server.handle_request()  # Maneja las peticiones del servidor

                    # Inicia el servidor en un nuevo hilo
                    self.server_thread = threading.Thread(target=run_server)
                    self.server_thread.start()
                    return
            print("Acceso denegado. Solo los administradores pueden iniciar el servidor.")
        else:
            print("No hay ningún usuario en sesión.")

    def apagar_servidor(self):
        """Apaga el servidor XML-RPC."""
        if self.sesion and 'nombre_usuario' in self.sesion:
            nombre_usuario = self.sesion['nombre_usuario']
            # Verificamos si el usuario tiene permisos de administrador
            for usuario in self.usuarios:
                if usuario.nombre_usuario == nombre_usuario and usuario.admin:
                    self.running = False  # Cambia el estado a no en ejecución
                    if self.server:
                        self.server.server_close()  # Cierra el servidor
                        self.server_thread.join()  # Espera a que el hilo termine
                        print("Servidor apagado.")
                    return
            print("Acceso denegado. Solo los administradores pueden apagar el servidor.")
        else:
            print("No hay ningún usuario en sesión.")

    def __repr__(self):
        return f"Servidor con {len(self.usuarios)} usuarios."
    
#####################################################################################################################################################################    
    def recibir_comando_cliente(self, comando):
        self.comando_recibido = comando
        # return Alguna respuesta del servidor
#####################################################################################################################################################################

    class MyRequestHandler(SimpleXMLRPCRequestHandler):
        
        def handle(self):
            # Capturar la IP del cliente y almacenarla en el servidor
            servidor = self.server.instance
            servidor.ip_cliente = self.client_address[0]
            super().handle()  # Procesar normalmente la solicitud

    def get_ip(self):
        """Devuelve la última IP de cliente conectada"""
        return self.ip_cliente
