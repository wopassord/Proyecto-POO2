import socket
import time

from interprete_gcode import SimuladorRobot
class ABBSimClient:
    def __init__(self, host='localhost', port=8001):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))
        self.coordinates = []

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
            
if __name__ == "__main__":
    simuladorrobot = SimuladorRobot()
    client = ABBSimClient()
    movimientos = []
    with open("instrucciones1.gcode", "r") as file:
        contenido_gcode = file.read()
    simuladorrobot.procesar_gcode(contenido_gcode)
    print("Movimientos procesados:")
    client.coordinates = simuladorrobot.movimientos

    print(client.coordinates)
    client.send_all_coordinates(client.coordinates)
    client.close_connection()



