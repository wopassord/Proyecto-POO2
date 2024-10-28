from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from usuario import Usuario
from controlador import Controlador
import threading
import time

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
        self.controlador = Controlador()

    def get_estado_servidor(self):
        return self.running

    def get_sesion(self):
        return self.sesion
    
    def get_usuarios(self):
        return self.usuarios
    
    def get_comando_recibido(self):
        return self.comando_recibido
    
    def agregar_usuario(self, nombre_usuario, contrasena, admin):
        for usuario in self.usuarios:
            if nombre_usuario == usuario.nombre_usuario:
                print("El usuario ingresado ya existe, por favor, ingrese un usuario válido.")
                return  # Salimos del método si el usuario ya existe
        
        nuevo_usuario = Usuario(nombre_usuario, contrasena, admin)
        self.usuarios.append(nuevo_usuario)
        print(f"Usuario {nombre_usuario} agregado correctamente.")
        nuevo_usuario.guardar_usuarios_csv()

    def iniciar_sesion(self):
        while not self.sesion_iniciada:
            nombre_usuario = input("Ingrese el nombre de usuario (o 'salir' para cancelar): ")
            
            if nombre_usuario.lower() == "salir":
                print("Sesión cancelada.")
                return None
            
            usuario_encontrado = None
            for usuario in self.usuarios:
                if usuario.nombre_usuario == nombre_usuario:
                    usuario_encontrado = usuario
                    break
            
            if usuario_encontrado is None:
                print("El usuario ingresado no existe, por favor, ingrese un usuario válido.")
            else:
                contrasena = input("Ingrese la contraseña: ")
                if usuario_encontrado.contrasena == contrasena:
                    print(f"Bienvenido {nombre_usuario}!")
                    self.sesion_iniciada = True
                    self.sesion = {'nombre_usuario': nombre_usuario, 'contrasena': contrasena}
                else:
                    print("La contraseña ingresada es incorrecta. Pruebe nuevamente.")
        return None
    
    def cerrar_sesion(self):
        self.sesion_iniciada = False
        self.sesion = {}

    def iniciar_servidor(self, host="127.0.0.1", port=8080):
        """Inicia el servidor XML-RPC sin verificar la sesión de usuario."""
        print("Iniciando el servidor...")
        self.running = True  # Cambia el estado a en ejecución

        def run_server():
            self.server = SimpleXMLRPCServer((host, port), requestHandler=self.MyRequestHandler)
            self.server.register_instance(self)
            # Registrar las funciones remotas que el cliente puede invocar
            self.server.register_function(self.saludo_personalizado, "saludo_personalizado")
            self.server.register_function(self.apagar_servidor, "apagar_servidor")  # Registramos el apagado
            self.server.register_function(self.subir_archivo_gcode, "subir_archivo_gcode")

            print(f"Servidor XML-RPC escuchando en {host}:{port}...")
            while self.running:
                self.server.handle_request()

        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.start()

        print("Servidor iniciado correctamente en un hilo separado.")
        
    def apagar_servidor(self):
        """Apaga el servidor XML-RPC de forma controlada."""
        print("El servidor se está apagando...")
        response = "El servidor se apagará en unos momentos."

        # Ejecutar el shutdown suave en un hilo separado
        threading.Thread(target=self.shutdown_servidor).start()

        return response

    def shutdown_servidor(self):
        """Cerrar el servidor después de un pequeño retraso."""
        time.sleep(1)  # Esperar para dar tiempo al cliente
        self.running = False
        if self.server:
            self.server.server_close()
            self.server_thread.join()
        print("Servidor apagado correctamente.")

    def saludo_personalizado(self, nombre):
        return f"Hola {nombre}, ¡conexión exitosa con el servidor XML-RPC!"
    
    
    
    def subir_archivo_gcode(self, nombre_archivo, contenido_archivo):
        try:
            with open(nombre_archivo, 'w') as f:
                f.write(contenido_archivo)

            print(f"Archivo {nombre_archivo} recibido.")
            print(f"Contenido del archivo: \n{contenido_archivo}")
            
            return f"Archivo {nombre_archivo} recibido y almacenado correctamente."
        except Exception as e:
            return f"Error al guardar el archivo: {str(e)}"

    def __repr__(self):
        return f"Servidor con {len(self.usuarios)} usuarios."
    
#####################################################################################################################################################################    
    def recibir_comando_cliente(self, comando):
        self.comando_recibido = comando
        if comando in list(range(1,7)):
            respuesta = Controlador.procesar_comando(comando)
        else:
            respuesta = Controlador.procesar_comando(comando)
        return respuesta
#####################################################################################################################################################################


    class MyRequestHandler(SimpleXMLRPCRequestHandler):
        def handle(self):
            servidor = self.server.instance
            servidor.ip_cliente = self.client_address[0]
            super().handle()

    def get_ip(self):
        return self.ip_cliente
