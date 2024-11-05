import socket
import time
import numpy as np


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
                if not isinstance(coord, np.ndarray):  # Verificar tipo de coord
                    coord = np.array(coord, dtype=np.float64)  # Convertir a array de floats si no lo es
                message = ", ".join(map(str, coord)) + "\n"
                client_socket.sendall(message.encode('utf-8'))
                print("Coordenada enviada:", message)
                time.sleep(0.1)
            client_socket.sendall("fin_gif\n".encode('utf-8'))
            print("Se enviaron todas las coordenadas. Finalizando guardado del GIF.")