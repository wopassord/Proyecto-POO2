import socket
import time

from interprete_gcode import SimuladorRobot
class ABBSimClient:
    def __init__(self, host='localhost', port=8001):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.coordinates = None

    def send_coordinate(self, coordinate):
        """Envía una coordenada al servidor MATLAB."""
        message = coordinate + "\n"
        self.client_socket.sendall(message.encode('utf-8'))
        print("Coordenada enviada:", coordinate)

    def send_all_coordinates(self, coordinates_list):
        """Envía todas las coordenadas de la lista y envía el mensaje 'fin_gif' al final."""
        for coord in coordinates_list:
            self.send_coordinate(coord)
        # Enviar mensaje para indicar el final de la transmisión
        self.client_socket.sendall("fin_gif\n".encode('utf-8'))
        print("Se enviaron todas las coordenadas. Finalizando guardado del GIF.")

    def close_connection(self):
        """Envía el comando de salida y cierra la conexión."""
        self.client_socket.sendall("salir\n".encode('utf-8'))
        print("Comando de salida enviado. Finalizando cliente...")
        self.client_socket.close()

    def format_coordinates(self, movimientos):
        """
        Convierte las coordenadas almacenadas en la lista `movimientos` de SimuladorRobot
        a un formato de texto adecuado para enviar al servidor MATLAB.
        """
        self.coordinates = []
        for pos in movimientos:
            coord_str = f"{pos[0]*0.001},{pos[1]*0.001},{pos[2]*0.001}"
            self.coordinates.append(coord_str)
            
if __name__ == "__main__":
    simuladorrobot = SimuladorRobot()
    client = ABBSimClient()
    with open("instrucciones1.gcode", "r") as file:
        contenido_gcode = file.read()
    simuladorrobot.procesar_gcode(contenido_gcode)
    print("Movimientos procesados:")
    for movimiento in simuladorrobot.movimientos:
        print(movimiento)
    movimientos = [
        (0.04, 0.02, 0.1),
        (-0.05, -0.01, 0.2),
        (0.06, -0.03, 0.15),
        (-0.04, 0.05, 0.18),
        (0.03, -0.02, 0.12),
        (-0.02, 0.04, 0.16)
    ]
    client.format_coordinates(movimientos)
    print(client.coordinates)
    client.send_all_coordinates(client.coordinates)
    client.close_connection()

        # Crear una instancia de SimuladorRobot
    simulador = SimuladorRobot()

    # Leer el archivo G-Code


    # Procesar el archivo G-Code


    # Mostrar los movimientos procesados

