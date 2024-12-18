from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from usuario import (Usuario,)  # Asegúrate de tener la clase Usuario en un archivo separado llamado usuario.py
import csv
import threading
import csv
from interprete_gcode import UtilGcode


class Servidor:
    def __init__(self):
        self.usuarios = self.leer_usuarios_csv() 
        self.sesion_iniciada = False  # Estado de la sesión de usuario
        self.sesion = {}  # Información de la sesión actual
        self.running = False  # Estado del servidor
        self.server = None  # Instancia del servidor XML-RPC
        self.server_thread = None  # Hilo para el servidor XML-RPC
        self.interface_thread = None  # Hilo para la interfaz de usuario
        self.ip_cliente = None  
        self.comando_recibido = None  
        self.interfaz = None  # InterfazServidor, se asignará desde main.py
        self.gcode = UtilGcode()

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
                self.server.register_function(self.iniciar_sesion_cliente, "iniciar_sesion")
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
            exito = 1
            return exito


    def leer_usuarios_csv(self, archivo="usuarios_servidor_uno.csv"):
        try:
            with open(archivo, mode="r", newline="") as csvfile:
                reader = csv.reader(csvfile)
                usuarios = []
                for row in reader:

                    nombre_usuario, contrasena, admin, token = row
                    admin = (
                        admin.lower() == "true"
                    )  # Convertir el valor del campo admin a booleano
                    usuarios.append(Usuario(nombre_usuario, contrasena, admin, token))

                return usuarios

        except FileNotFoundError:
            print(f"El archivo {archivo} no existe o no hay usuarios disponibles.")
            return []
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
            return []

    def apagar_servidor(self):
        if self.interfaz.verificar_sesion_admin() == True:
            """Apaga el servidor XML-RPC de forma controlada."""
            print("Apagando el servidor...")
            self.running = False
            if self.server:
                self.server.server_close()
            if self.server_thread:
                self.server_thread.join()  # Espera a que el hilo del servidor termine, se puede seguir escribiendo en la terminal del "servidor"
            print("Servidor apagado")
            exito = 1
            return exito
        else:
            exito = 0
            return exito


    def guardar_usuario_csv(
        self,
        nombre_usuario,
        contrasena,
        admin=False,
        token = None,
        archivo="usuarios_servidor_uno.csv",
    ):

        """Guarda un usuario nuevo en el archivo CSV."""
        with open(archivo, mode='a', newline='\n') as csvfile:

            writer = csv.writer(csvfile)
            writer.writerow([nombre_usuario, contrasena, str(admin), token])
        print(f"Usuario {nombre_usuario} agregado al archivo CSV.")

    def saludo_personalizado(self, nombre):
        """Retorna un saludo personalizado al cliente."""
        return f"Hola {nombre}, ¡conexión exitosa con el servidor XML-RPC!"
    
    def subir_archivo_gcode(self, nombre_archivo, contenido_archivo, returnBuffer=False):
        if self.interfaz.modo_trabajo == "automatico":
            try:
                self.gcode.subir_archivo_gcode(nombre_archivo, contenido_archivo, returnBuffer)
                return self.interfaz.cargar_y_ejecutar_archivo_gcode(contenido_archivo)
            except Exception as e:
                return f"Se produjo el siguiente error: {e}"
        else:
            return "Esta acciOn solo esta disponible en modo automatico. Cambie el modo de trabajo a automatico para proceder."

    def recibir_comando_cliente(self, comando):
        """Recibe un comando desde el cliente y lo procesa."""
        if self.interfaz:
            return self.interfaz.recibir_comando_cliente(comando)
        else:
            return "Error: Interfaz no disponible"

    # Clase para manejar solicitudes XML-RPC, obteniendo la IP del cliente
    class MyRequestHandler(SimpleXMLRPCRequestHandler):
        def handle(self):
            servidor = self.server.instance
            servidor.ip_cliente = self.client_address[0]
            super().handle()

    def agregar_usuario(self, nombre_usuario, contrasena, admin=False, token = None):
        """Agrega un usuario nuevo al sistema."""
        nuevo_usuario = Usuario(nombre_usuario, contrasena, admin, token)
        self.usuarios.append(nuevo_usuario)
        print(f"Usuario {nombre_usuario} agregado correctamente.")

        # Llamar a guardar_usuario_csv para escribir en el archivo CSV
        self.guardar_usuario_csv(nombre_usuario, contrasena, admin, token)

    def iniciar_sesion(self):
        """Inicia una sesión de usuario."""
        while not self.sesion_iniciada:
            nombre_usuario = input(
                "Ingrese el nombre de usuario (o 'salir' para cancelar): "
            )
            if nombre_usuario.lower() == "salir":
                print("Sesión cancelada.")
                return None

            # Leer usuarios desde el archivo CSV
            self.usuarios = self.leer_usuarios_csv()

            # Buscar el usuario en la lista obtenida del archivo CSV
            usuario_encontrado = next(
                (u for u in self.usuarios if u.nombre_usuario == nombre_usuario), None
            )
            if not usuario_encontrado:
                print(
                    "El usuario ingresado no existe, por favor, ingrese un usuario válido."
                )
                continue

            # Verificar contraseña
            contrasena = input("Ingrese la contraseña: ")
            if usuario_encontrado.contrasena == contrasena:
                print(f"Bienvenido {nombre_usuario}!")
                self.sesion_iniciada = True
                # Guardar los detalles de la sesión, incluido el estado de administrador
                self.sesion = {
                    'nombre_usuario': nombre_usuario,
                    'contrasena': contrasena,
                    'admin': usuario_encontrado.admin  # Guardar si es administrador o no

                }
            else:
                print("La contraseña ingresada es incorrecta. Pruebe nuevamente.")
    
    def iniciar_sesion_cliente(self, nombre_usuario, contrasena):
        """Inicia una sesión de usuario para un cliente que envía los datos directamente."""
        if self.sesion_iniciada:
            return False, "Ya hay una sesión iniciada."

        # Leer usuarios desde el archivo CSV
        self.usuarios = self.leer_usuarios_csv()

        # Buscar el usuario en la lista obtenida del archivo CSV
        usuario_encontrado = next(
            (u for u in self.usuarios if u.nombre_usuario == nombre_usuario), None
        )
        if not usuario_encontrado:
            return False, "El usuario ingresado no existe."

        # Verificar contraseña
        if usuario_encontrado.contrasena == contrasena:
            self.sesion_iniciada = True
            # Guardar los detalles de la sesión, incluido el estado de administrador
            self.sesion = {
                'nombre_usuario': nombre_usuario,
                'admin': usuario_encontrado.admin
            }
            return True, "Bienvenido " + nombre_usuario
        else:
            return False, "La contraseña ingresada es incorrecta."

    def cerrar_sesion(self):
        """Cierra la sesión del usuario actual."""
        self.sesion_iniciada = False
        self.sesion = {}
        exito = 1
        return exito

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