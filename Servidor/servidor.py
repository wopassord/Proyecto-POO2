from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from usuario import Usuario  # Asegúrate de tener la clase Usuario en un archivo separado llamado usuario.py
from controlador import Controlador  # Clase que controla el robot, por ejemplo
import threading
import time

class Servidor:
    def __init__(self):
        self.usuarios = []  # Lista de usuarios
        self.sesion_iniciada = False  # Estado de la sesión de usuario
        self.sesion = {}  # Información de la sesión actual
        self.running = False  # Estado del servidor
        self.server = None  # Instancia del servidor XML-RPC
        self.server_thread = None  # Hilo para el servidor XML-RPC
        self.interface_thread = None  # Hilo para la interfaz de usuario
        self.ip_cliente = None  # Última IP de cliente conectada
        self.comando_recibido = None  # Último comando recibido de un cliente
        self.controlador = Controlador()  # Instancia del controlador del robot
        self.interfaz = None  # InterfazServidor, se asignará desde main.py

    def asignar_interfaz(self, interfaz):
        """Asigna la instancia de InterfazServidor."""
        self.interfaz = interfaz

    def iniciar_servidor(self, host="127.0.0.1", port=8080):
        """Inicia el servidor XML-RPC en un hilo separado."""
        print("Iniciando el servidor XML-RPC...")
        self.running = True

        def run_server():
            self.server = SimpleXMLRPCServer((host, port), requestHandler=self.MyRequestHandler)
            self.server.register_instance(self)
            # Registrar funciones que pueden ser invocadas remotamente
            self.server.register_function(self.saludo_personalizado, "saludo_personalizado")
            self.server.register_function(self.apagar_servidor, "apagar_servidor")
            self.server.register_function(self.subir_archivo_gcode, "subir_archivo_gcode")
            print(f"Servidor XML-RPC escuchando en {host}:{port}...")

            # Bucle para manejar solicitudes de clientes XML-RPC
            while self.running:
                self.server.handle_request()

        # Creación y arranque del hilo del servidor XML-RPC
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.start()
        print("Servidor XML-RPC iniciado en un hilo separado.")

    def iniciar_interfaz(self):
        """Inicia la interfaz de usuario en la terminal en un hilo separado."""
        print("Iniciando interfaz de usuario en la terminal...")

        def run_interface():
            if self.interfaz:
                self.interfaz.administrar_comandos()  # Llama al método para manejar comandos en la terminal
            else:
                print("Interfaz no asignada. Usa asignar_interfaz() antes de iniciar la interfaz.")

        # Creación y arranque del hilo de la interfaz de usuario
        self.interface_thread = threading.Thread(target=run_interface)
        self.interface_thread.start()
        print("Interfaz de usuario iniciada en un hilo separado.")

    def apagar_servidor(self):
        """Apaga el servidor XML-RPC de forma controlada."""
        print("Apagando el servidor...")
        self.running = False
        if self.server:
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join()  # Espera a que el hilo del servidor termine
        if self.interface_thread:
            self.interface_thread.join()  # Espera a que el hilo de la interfaz termine
        print("Servidor apagado y ambos hilos detenidos.")

    # Métodos XML-RPC
    def saludo_personalizado(self, nombre):
        """Retorna un saludo personalizado al cliente."""
        return f"Hola {nombre}, ¡conexión exitosa con el servidor XML-RPC!"

    def subir_archivo_gcode(self, nombre_archivo, contenido_archivo):
        """Guarda un archivo G-Code enviado por el cliente."""
        try:
            with open(nombre_archivo, 'w') as f:
                f.write(contenido_archivo)
            print(f"Archivo {nombre_archivo} recibido y guardado.")
            return f"Archivo {nombre_archivo} recibido y almacenado correctamente."
        except Exception as e:
            print(f"Error al guardar el archivo: {e}")
            return f"Error al guardar el archivo: {str(e)}"

    def recibir_comando_cliente(self, comando):
        """Recibe un comando desde el cliente y lo procesa."""
        self.comando_recibido = comando
        respuesta = self.controlador.procesar_comando(comando) if comando not in range(1, 7) else None
        self.comando_recibido = None
        return respuesta

    # Clase para manejar solicitudes XML-RPC, obteniendo la IP del cliente
    class MyRequestHandler(SimpleXMLRPCRequestHandler):
        def handle(self):
            servidor = self.server.instance
            servidor.ip_cliente = self.client_address[0]
            super().handle()

    # Métodos de gestión de usuarios
    def agregar_usuario(self, nombre_usuario, contrasena, admin):
        """Agrega un usuario nuevo al sistema."""
        if any(u.nombre_usuario == nombre_usuario for u in self.usuarios):
            print("El usuario ingresado ya existe.")
            return
        nuevo_usuario = Usuario(nombre_usuario, contrasena, admin)
        self.usuarios.append(nuevo_usuario)
        print(f"Usuario {nombre_usuario} agregado correctamente.")
        nuevo_usuario.guardar_usuarios_csv()

    def iniciar_sesion(self):
        """Inicia una sesión de usuario."""
        while not self.sesion_iniciada:
            nombre_usuario = input("Ingrese el nombre de usuario (o 'salir' para cancelar): ")
            if nombre_usuario.lower() == "salir":
                print("Sesión cancelada.")
                return None

            # Buscar el usuario
            usuario_encontrado = next((u for u in self.usuarios if u.nombre_usuario == nombre_usuario), None)
            if not usuario_encontrado:
                print("El usuario ingresado no existe, por favor, ingrese un usuario válido.")
                continue

            # Verificar contraseña
            contrasena = input("Ingrese la contraseña: ")
            if usuario_encontrado.contrasena == contrasena:
                print(f"Bienvenido {nombre_usuario}!")
                self.sesion_iniciada = True
                self.sesion = {'nombre_usuario': nombre_usuario, 'contrasena': contrasena}
            else:
                print("La contraseña ingresada es incorrecta. Pruebe nuevamente.")

    def cerrar_sesion(self):
        """Cierra la sesión del usuario actual."""
        self.sesion_iniciada = False
        self.sesion = {}

    # Getters adicionales
    def get_estado_servidor(self):
        return self.running

    def get_sesion(self):
        return self.sesion

    def get_usuarios(self):
        return self.usuarios

    def get_comando_recibido(self):
        return self.comando_recibido

    def __repr__(self):
        return f"Servidor con {len(self.usuarios)} usuarios."










'''''''''
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from usuario import Usuario
from controlador import Controlador
from interfazServidor import InterfazServidor
import threading

class Servidor:
    def __init__(self):
        self.usuarios = []
        self.sesion_iniciada = False
        self.sesion = {}
        self.running = False
        self.server = None
        self.server_thread = None
        self.interface_thread = None
        self.ip_cliente = None
        self.comando_recibido = None
        self.controlador = Controlador()
        self.interfaz = InterfazServidor()

    def iniciar_servidor(self, host="127.0.0.1", port=8080):
        """Inicia el servidor XML-RPC en un hilo separado."""
        print("Iniciando el servidor XML-RPC...")
        self.running = True

        def run_server():
            self.server = SimpleXMLRPCServer((host, port), requestHandler=self.MyRequestHandler)
            self.server.register_instance(self)
            self.server.register_function(self.saludo_personalizado, "saludo_personalizado")
            self.server.register_function(self.apagar_servidor, "apagar_servidor")
            self.server.register_function(self.subir_archivo_gcode, "subir_archivo_gcode")
            print(f"Servidor XML-RPC escuchando en {host}:{port}...")
            while self.running:
                self.server.handle_request()

        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.start()
        print("Servidor XML-RPC iniciado en un hilo separado.")

    def iniciar_interfaz(self):
        """Inicia la interfaz de usuario en la terminal en un hilo separado."""
        print("Iniciando interfaz de usuario en la terminal...")

        def run_interface():
            self.interfaz.administrar_comandos()
        
        self.interface_thread = threading.Thread(target=run_interface)
        self.interface_thread.start()
        print("Interfaz de usuario iniciada en un hilo separado.")

    def apagar_servidor(self):
        """Apaga el servidor XML-RPC de forma controlada."""
        print("El servidor se está apagando...")
        self.running = False
        if self.server:
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join()
        if self.interface_thread:
            self.interface_thread.join()
        print("Servidor apagado y ambos hilos detenidos.")

    def saludo_personalizado(self, nombre):
        return f"Hola {nombre}, ¡conexión exitosa con el servidor XML-RPC!"

    def subir_archivo_gcode(self, nombre_archivo, contenido_archivo):
        try:
            with open(nombre_archivo, 'w') as f:
                f.write(contenido_archivo)
            print(f"Archivo {nombre_archivo} recibido.")
            return f"Archivo {nombre_archivo} recibido y almacenado correctamente."
        except Exception as e:
            return f"Error al guardar el archivo: {str(e)}"

    def recibir_comando_cliente(self, comando):
        self.comando_recibido = comando
        respuesta = Controlador.procesar_comando(comando) if comando not in range(1, 7) else None
        self.comando_recibido = None
        return respuesta

    class MyRequestHandler(SimpleXMLRPCRequestHandler):
        def handle(self):
            servidor = self.server.instance
            servidor.ip_cliente = self.client_address[0]
            super().handle()

    def get_estado_servidor(self):
        return self.running

    def get_sesion(self):
        return self.sesion

    def get_usuarios(self):
        return self.usuarios

    def get_comando_recibido(self):
        return self.comando_recibido

    def agregar_usuario(self, nombre_usuario, contrasena, admin):
        if any(u.nombre_usuario == nombre_usuario for u in self.usuarios):
            print("El usuario ingresado ya existe, por favor, ingrese un usuario válido.")
            return
        
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
            usuario_encontrado = next((u for u in self.usuarios if u.nombre_usuario == nombre_usuario), None)
            if not usuario_encontrado:
                print("El usuario ingresado no existe, por favor, ingrese un usuario válido.")
                continue
            contrasena = input("Ingrese la contraseña: ")
            if usuario_encontrado.contrasena == contrasena:
                print(f"Bienvenido {nombre_usuario}!")
                self.sesion_iniciada = True
                self.sesion = {'nombre_usuario': nombre_usuario, 'contrasena': contrasena}
            else:
                print("La contraseña ingresada es incorrecta. Pruebe nuevamente.")
    
    def cerrar_sesion(self):
        self.sesion_iniciada = False
        self.sesion = {}

    def __repr__(self):
        return f"Servidor con {len(self.usuarios)} usuarios."

    '''