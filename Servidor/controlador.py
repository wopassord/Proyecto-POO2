import serial
import time
import threading
import queue


class Controlador:
    def __init__(self):
        self.estado_robot = False
        self.estado_motores = False
        self.baudrate = 115200
        self.puerto_COM = "COM7"
        self.arduino = None
        self.hilo_lectura = None
        self.cola_respuestas = queue.Queue()

    def get_estado_robot(self):
        return self.estado_robot

    def get_estado_motores(self):
        return self.estado_motores

    def cambiar_parametros_comunicacion(self, baudrate, puerto_COM):
        if self.estado_robot:
            self.desconectar_robot()
        self.baudrate = int(baudrate)
        self.puerto_COM = puerto_COM
        print(
            f"Parámetros de comunicación cambiados: Baudrate={self.baudrate}, Puerto={self.puerto_COM}"
        )

    def conectar_robot(self):
        try:
            self.arduino = serial.Serial(self.puerto_COM, self.baudrate, timeout=1)
            self.estado_robot = True
            time.sleep(2)
            self.arduino.reset_input_buffer()
            respuesta = f"Conexión establecida en {self.puerto_COM} con baudrate {self.baudrate}."
            print(respuesta)

            # Iniciar hilo para leer respuestas
            self.hilo_lectura = threading.Thread(target=self.leer_respuesta)
            self.hilo_lectura.start()
            exito = 1
            return respuesta, exito
        except serial.SerialException:
            respuesta = f"Error al conectar: Verifique que el puerto {self.puerto_COM} esté disponible y correcto."
            print(respuesta)
            self.estado_robot = False
            self.arduino = None
            exito = 0
        return respuesta, exito

    def desconectar_robot(self):
        if self.arduino and self.arduino.is_open:
            self.estado_robot = False
            if self.hilo_lectura and self.hilo_lectura.is_alive():
                self.hilo_lectura.join()
            self.arduino.close()
            respuesta = "Robot desconectado."
            exito = 1
        else:
            respuesta = "El robot ya está desconectado o no había conexión."
            exito = 0
        print(respuesta)
        return respuesta, exito

    def activar_motores(self):
        if self.estado_robot:
            # Enviar el comando M17 al Arduino sin esperar respuesta
            self.enviar_comando("M17")
            self.estado_motores = True
            respuesta = "MOTORES ACTIVADOS."
            exito = 1
        else:
            respuesta = "No se pueden activar los motores. El robot no está conectado."
            exito = 0
        print(respuesta)
        return respuesta, exito

    def desactivar_motores(self):
        if self.estado_robot:
            # Enviar el comando M18 al Arduino sin esperar respuesta
            self.enviar_comando("M18")
            self.estado_motores = False
            respuesta = "MOTORES DESACTIVADOS."
            exito = 1
        else:
            respuesta = (
                "No se pueden desactivar los motores. El robot no está conectado."
            )
            exito = 0
        print(respuesta)

        return respuesta, exito

    def enviar_comando(self, comando, mostrar=True):
        if self.estado_robot:
            try:
                if comando == "G21": #firmware de arduino no acusa respuesta, incluimos esta respuesta interna del servidor
                    respuesta = "Unidades establecidas en [mm]."
                    print(respuesta)
                    exito = 1
                    return respuesta, exito
                # Verifica si el comando es 'M17' o 'M18' para evitar mostrar "No se recibió respuesta"

                elif comando in ['M17', 'M18']:
                    if comando == 'M17':
                        self.arduino.write((comando + '\r\n').encode('latin-1'))
                        time.sleep(0.1)
                        respuesta = "MOTORES ACTIVADOS." #firmware de arduino no acusa respuesta, incluimos esta respuesta interna del servidor
                        print(respuesta)
                        exito = 1
                    elif comando == 'M18': #firmware de arduino no acusa respuesta, incluimos esta respuesta interna del servidor
                        self.arduino.write((comando + '\r\n').encode('latin-1'))
                        time.sleep(0.1)
                        respuesta = "MOTORES DESACTIVADOS."
                        print(respuesta)
                        exito = 1
                    return respuesta, exito
                else:
                    self.arduino.write(
                        (comando + "\r\n").encode("latin-1")
                    )  # Enviar comando en formato de bytes
                    time.sleep(0.1)  # Tiempo de espera para recibir respuesta
                    respuesta = self.leer_respuesta()
                    if respuesta:
                        exito = 1
                        if mostrar:
                            print(f"Respuesta recibida: {respuesta}")
                        
                    else:
                        exito = 0
                        if mostrar:
                            print("No se recibió respuesta del robot.")
                        
                    return respuesta, exito
            except Exception as e:
                respuesta = f"Error al enviar comando: {e}"
                exito = 0
                if mostrar:
                    print(respuesta)
                return respuesta, exito
        else:
            respuesta = "No se puede enviar el comando. El robot no está conectado."
            exito = 0
            if mostrar:
                print(respuesta)
        return respuesta, exito

    def leer_respuesta(self):
        try:
            respuesta_completa = ""
            while self.arduino and self.arduino.in_waiting > 0:
                respuesta = self.arduino.read(self.arduino.in_waiting).decode("latin-1")
                respuesta_completa += respuesta
            return (
                respuesta_completa.replace("ñ", "A").strip()
                if respuesta_completa
                else None
            )
        except serial.SerialException as e:
            print(f"Error de comunicación: {e}")
        except Exception as e:
            print(f"Error inesperado al leer respuestas: {e}")

    def procesar_respuestas_arduino(self):
        while not self.cola_respuestas.empty():
            respuesta = self.cola_respuestas.get()
            print(f"Respuesta del Arduino: {respuesta}")
