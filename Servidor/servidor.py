from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from usuario import Usuario  # Asegúrate de tener la clase Usuario en un archivo separado llamado usuario.py
from controlador import Controlador  # Clase que controla el robot, por ejemplo
import csv
import interfazServidor
import threading
import csv
import re
import numpy as np
import matplotlib.pyplot as plt


class SimuladorRobot:
    def __init__(self):
        self.movimientos = []  # Lista para almacenar las posiciones de cada movimiento
        self.posicion_actual = np.array([60, 0, 260])  # Posición inicial del robot en el origen

    def procesar_gcode(self, contenido_gcode):
        """
        Lee y procesa el contenido de un archivo G-Code.
        Extrae los comandos G1 con coordenadas X, Y, Z para determinar las posiciones del robot.
        """
        for linea in contenido_gcode.splitlines():
            # Buscar el comando G1 que indica movimiento a una posición específica
            if linea.startswith("G1"):
                x = self.posicion_actual[0]
                y = self.posicion_actual[1]
                z = self.posicion_actual[2]
                
                # Extraer coordenadas X, Y, Z si están presentes en la línea
                match_x = re.search(r"X([-+]?\d*\.\d+|\d+)", linea)
                match_y = re.search(r"Y([-+]?\d*\.\d+|\d+)", linea)
                match_z = re.search(r"Z([-+]?\d*\.\d+|\d+)", linea)

                if match_x:
                    x = float(match_x.group(1))
                if match_y:
                    y = float(match_y.group(1))
                if match_z:
                    z = float(match_z.group(1))
                
                # Actualizar la posición actual
                nueva_posicion = np.array([x, y, z])
                self.movimientos.append(nueva_posicion)
                self.posicion_actual = nueva_posicion



def visualizar_movimientos(self):
    """
    Crea una visualización en 3D de los movimientos del robot y del modelo ABB IRB 460.
    """
    # Figura para la trayectoria del robot
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111, projection='3d')

    # Convertir la lista de movimientos en un array para fácil manipulación
    movimientos_array = np.array(self.movimientos)

    # Graficar la trayectoria del robot
    ax1.plot(movimientos_array[:, 0], movimientos_array[:, 1], movimientos_array[:, 2], marker='o', label="Trayectoria")
    
    # Representar articulaciones como vectores unitarios (versores)
    for i in range(1, len(movimientos_array)):
        origen = movimientos_array[i - 1]
        destino = movimientos_array[i]
        vector = destino - origen
        versor = vector / np.linalg.norm(vector)  # Normalizar para obtener el versor

        # Dibujar el versor (articulación) con una flecha
        ax1.quiver(origen[0], origen[1], origen[2], versor[0], versor[1], versor[2],
                   length=1, color='r', normalize=True)

    # Configuración de los ejes
    ax1.set_xlabel("X")
    ax1.set_ylabel("Y")
    ax1.set_zlabel("Z")
    ax1.set_title("Simulación de Movimientos del Robot")
    plt.legend()
    plt.show()


class Servidor:
    def __init__(self):
        self.usuarios = self.leer_usuarios_csv()  # Lista de usuarios
        self.sesion_iniciada = False  # Estado de la sesión de usuario
        self.sesion = {}  # Información de la sesión actual
        self.running = False  # Estado del servidor
        self.server = None  # Instancia del servidor XML-RPC
        self.server_thread = None  # Hilo para el servidor XML-RPC
        self.interface_thread = None  # Hilo para la interfaz de usuario
        self.ip_cliente = None  # Última IP de cliente conectada
        self.comando_recibido = None  # Último comando recibido de un cliente
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

    def leer_usuarios_csv(self, archivo='usuarios_servidor_uno.csv'):
        try:
            with open(archivo, mode='r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                usuarios = []
                for row in reader:
                    nombre_usuario, contrasena, admin = row
                    admin = admin.lower() == 'true'  # Convertir el valor del campo admin a booleano
                    usuarios.append(Usuario(nombre_usuario, contrasena, admin))
                
                return usuarios
        
        except FileNotFoundError:
            print(f"El archivo {archivo} no existe o no hay usuarios disponibles.")
            return []
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
            return []

    def apagar_servidor(self):
        """Apaga el servidor XML-RPC de forma controlada."""
        print("Apagando el servidor...")
        self.running = False
        if self.server:
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join()  # Espera a que el hilo del servidor termine, se puede seguir escribiendo en la terminal del "servidor"
        print("Servidor apagado")

    def guardar_usuario_csv(self, nombre_usuario, contrasena, admin=False, archivo='usuarios_servidor_uno.csv'):
        """Guarda un usuario nuevo en el archivo CSV."""
        with open(archivo, mode='a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([nombre_usuario, contrasena, str(admin)])
        print(f"Usuario {nombre_usuario} agregado al archivo CSV.")
    
    # Métodos XML-RPC
    def saludo_personalizado(self, nombre):
        """Retorna un saludo personalizado al cliente."""
        return f"Hola {nombre}, ¡conexión exitosa con el servidor XML-RPC!"

    #Visualizacion 3D robot:


    def subir_archivo_gcode(self, nombre_archivo, contenido_archivo):
        """Guarda un archivo G-Code enviado por el cliente."""
        try:
            with open(nombre_archivo, 'w') as f:
                f.write(contenido_archivo)
            print(f"Archivo {nombre_archivo} recibido.")
            print(f"Contenido del archivo: \n{contenido_archivo}")

            simulador = SimuladorRobot()
            simulador.procesar_gcode(contenido_archivo)
            simulador.visualizar_movimientos()

            return f"Archivo {nombre_archivo} recibido y almacenado correctamente."
        
            
        except Exception as e:
            print(f"Error al guardar el archivo: {str(e)}")
            return "Error al subir el archivo"

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

    def agregar_usuario(self, nombre_usuario, contrasena, admin=False):
        """Agrega un usuario nuevo al sistema."""
        nuevo_usuario = Usuario(nombre_usuario, contrasena, admin)
        self.usuarios.append(nuevo_usuario)
        print(f"Usuario {nombre_usuario} agregado correctamente.")

        # Llamar a guardar_usuario_csv para escribir en el archivo CSV
        self.guardar_usuario_csv(nombre_usuario, contrasena, admin)



    def iniciar_sesion(self):
        """Inicia una sesión de usuario."""
        while not self.sesion_iniciada:
            nombre_usuario = input("Ingrese el nombre de usuario (o 'salir' para cancelar): ")
            if nombre_usuario.lower() == "salir":
                print("Sesión cancelada.")
                return None

            # Leer usuarios desde el archivo CSV
            self.usuarios = self.leer_usuarios_csv()

            # Buscar el usuario en la lista obtenida del archivo CSV
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
