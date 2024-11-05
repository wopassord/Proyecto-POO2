import socket
import time
from interprete_gcode import SimuladorRobot

class ABBSimClient:
    def __init__(self, host='localhost', port=8001):
        self.host = host
        self.port = port

    def send_coordinate(self, coordinate):
        """Envía una coordenada al servidor MATLAB."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.host, self.port))
            message = coordinate + "\n"
            client_socket.sendall(message.encode('utf-8'))
            print("Coordenada enviada:", coordinate)

    def send_all_coordinates(self, coordinates_list):
        """Envía todas las coordenadas de la lista y envía el mensaje 'fin_gif' al final."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((self.host, self.port))
            for coord in coordinates_list:
                message = coord + "\n"
                client_socket.sendall(message.encode('utf-8'))
                print("Coordenada enviada:", coord)
                time.sleep(0.1)  # Pausa entre mensajes
            # Enviar mensaje para indicar el final de la transmisión
            client_socket.sendall("fin_gif\n".encode('utf-8'))
            print("Se enviaron todas las coordenadas. Finalizando guardado del GIF.")


if __name__ == "__main__":
    simuladorrobot = SimuladorRobot()
    client = ABBSimClient()
    movimientos = []
    with open("instrucciones5.gcode", "r") as file:
        contenido_gcode = file.read()
    simuladorrobot.procesar_gcode(contenido_gcode)
    print("Movimientos procesados:")
    client.coordinates = simuladorrobot.movimientos

    print(client.coordinates)
    client.send_all_coordinates(client.coordinates)



