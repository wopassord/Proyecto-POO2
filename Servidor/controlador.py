import serial
import time
import threading
import queue

class Controlador:

    def __init__(self):
        self.estado_robot = False
        self.estado_motores = False
        self.baudrate = 115200
        self.puerto_COM = 'COM7'
        self.arduino = None
        self.hilo_lectura = None
        self.cola_respuestas = queue.Queue()

    def get_estado_robot(self):
        return self.estado_robot
    
    def get_estado_motores(self):
        return self.estado_motores
    
    def cambiar_parametros_comunicacion(self, baudrate, puerto_COM):
        # Cerrar la conexión actual si está activa antes de cambiar los parámetros
        baudrate = int(baudrate)
        if self.estado_robot:
            self.desconectar_robot()

        self.baudrate = baudrate
        self.puerto_COM = puerto_COM
        print(f"Parámetros de comunicación cambiados: Baudrate={self.baudrate}, Puerto={self.puerto_COM}")

    def conectar_robot(self):
        try:
            self.arduino = serial.Serial(self.puerto_COM, self.baudrate, timeout=1)
            self.estado_robot = True
            time.sleep(2)
            self.arduino.reset_input_buffer()
            respuesta = f"Conexión establecida en {self.puerto_COM} con baudrate {self.baudrate}."
            print(respuesta)

            # Iniciar hilo para leer respuestas
            self.hilo_lectura = threading.Thread(target=self.leer_respuestas)
            self.hilo_lectura.start()

        except serial.SerialException:
            respuesta = f"Error al conectar: Verifique que el puerto {self.puerto_COM} esté disponible y correcto."
        except Exception as e:
            respuesta = f"Error al conectar: {e}"
        return respuesta

    def desconectar_robot(self):
        if self.arduino and self.arduino.is_open:
            self.estado_robot = False
            # Esperar que el hilo de lectura termine si existe y está en ejecución
            if self.hilo_lectura and self.hilo_lectura.is_alive():
                self.hilo_lectura.join()
            self.arduino.close()
            respuesta = "Robot desconectado."
        else:
            respuesta = "El robot ya está desconectado o no había conexión."
        print(respuesta)
        return respuesta

    def activar_motores(self):
        if self.estado_robot:
            respuesta = self.enviar_comando('M17')
            if respuesta:
                print("Motores activados.")
                self.estado_motores = True
            else:
                print("Error al activar motores.")
        else:
            respuesta = "No se pueden activar los motores. El robot no está conectado."
            print(respuesta)

        return respuesta
    
    def desactivar_motores(self):
        if self.estado_robot:
            respuesta = self.enviar_comando('M18')
            if respuesta:
                print("Motores desactivados.")
                self.estado_motores = False
            else:
                print("Error al desactivar motores.")
        else:
            respuesta = "No se pueden desactivar los motores. El robot no está conectado."
            print(respuesta)

        return respuesta

    def enviar_comando(self, comando):
        if self.estado_robot:
            try:
                self.arduino.write((comando + '\r\n').encode('latin-1'))  # Enviar comando en formato de bytes
                time.sleep(0.1)  # Tiempo de espera para recibir respuesta
                respuesta = self.leer_respuesta()
                if respuesta:
                    print(f"Respuesta recibida: {respuesta}")
                else:
                    print("No se recibió respuesta del robot.")
            except Exception as e:
                respuesta = f"Error al enviar comando: {e}"
                print(respuesta)
        else:
            respuesta = "No se puede enviar el comando. El robot no está conectado."
            print(respuesta)
        
        return respuesta
    
    def leer_respuesta(self):
        """Lee y devuelve la respuesta completa del Arduino, reemplazando caracteres no decodificados correctamente."""
        respuesta_completa = ""
        if self.arduino and self.arduino.in_waiting > 0:
            while self.arduino.in_waiting:
                respuesta = self.arduino.read(self.arduino.in_waiting).decode('latin-1')
                respuesta_completa += respuesta
                return respuesta_completa.replace("ñ", "A").strip()
            else:
                return None
            

    def procesar_respuestas_arduino(self):
        # Procesar respuestas disponibles en la cola
        while not self.cola_respuestas.empty():
            respuesta = self.cola_respuestas.get()
            print(f"Respuesta del Arduino: {respuesta}")