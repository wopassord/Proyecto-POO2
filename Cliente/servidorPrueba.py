from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import threading
import time
import sys

# Clase que maneja las solicitudes RPC
class MiServidorXMLRPC:
    def __init__(self, host="127.0.0.1", port=8080):
        # Configurar el servidor XML-RPC
        self.server = SimpleXMLRPCServer((host, port), requestHandler=RequestHandler)
        self.server.register_introspection_functions()

        # Registrar las funciones remotas
        self.server.register_function(self.saludo_personalizado, "saludo_personalizado")
        self.server.register_function(self.apagar_servidor, "apagar_servidor")
        self.server.register_function(self.subir_archivo_gcode, "subir_archivo_gcode")

    # Función remota para saludo personalizado
    def saludo_personalizado(self, nombre):
        return f"Hola {nombre}, ¡conexión exitosa con el servidor XML-RPC!"

    # Función remota para apagar el servidor
    def apagar_servidor(self):
        print("El servidor se está apagando...")
        response = "El servidor se apagará en unos momentos."
        # Ejecutar el shutdown suave en un hilo separado
        threading.Thread(target=self.shutdown_servidor).start()
        return response

    # Método para apagar el servidor
    def shutdown_servidor(self):
        time.sleep(1)  # Esperar para dar tiempo al cliente
        self.server.shutdown()  # Detener el servidor de manera controlada
        sys.exit(0)  # Salir de manera segura


     # Función remota para recibir y almacenar archivos G-Code
    def subir_archivo_gcode(self, nombre_archivo, contenido_archivo):
        try:
            with open(nombre_archivo, 'w') as f:
                f.write(contenido_archivo)

            print(f"Archivo {nombre_archivo} recibido.")
            print(f"Contenido del archivo: \n{contenido_archivo}")
            
            return f"Archivo {nombre_archivo} recibido y almacenado correctamente."
        except Exception as e:
            return f"Error al guardar el archivo: {str(e)}"

    # Método para iniciar el servidor
    def iniciar(self):
        print("Servidor XML-RPC escuchando en 127.0.0.1:8080...")
        self.server.serve_forever()


# Clase para manejar las solicitudes de manera segura
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Clase que gestiona la ejecución en un hilo separado
class ServidorHilo:
    def __init__(self):
        # Crear una instancia del servidor XML-RPC
        self.servidor = MiServidorXMLRPC()

    # Método para iniciar el servidor en un hilo separado
    def iniciar_en_hilo(self):
        servidor_thread = threading.Thread(target=self.servidor.iniciar)
        servidor_thread.start()


# Código principal para iniciar el servidor
if __name__ == "__main__":
    servidor_con_hilo = ServidorHilo()
    servidor_con_hilo.iniciar_en_hilo()