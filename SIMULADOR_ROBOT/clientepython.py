# import socket

# # Configuración del cliente
# host = 'localhost'  # La IP del servidor MATLAB
# port = 8001         # El mismo puerto que el servidor

# # Coordenadas predeterminadas en orden
# coordinates_list = [
#     "0.04,0.02,0.1",
#     "-0.05,-0.01,0.2",
#     "0.06,-0.03,0.15",
#     "-0.04,0.05,0.18",
#     "0.03,-0.02,0.12",
#     "-0.02,0.04,0.16"
# ]

# # Índice para rastrear la coordenada actual en la lista
# current_index = 0

# # Iniciar la conexión al servidor
# client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client_socket.connect((host, port))

# # Menú de opciones para el usuario
# while True:
#     print("Seleccione una opción:")
#     print("1. Enviar coordenada predeterminada")
#     print("2. Enviar comando de salida para finalizar el servidor")
#     option = input("Opción (1 o 2): ")

#     if option == "1":
#         # Enviar la coordenada predeterminada actual
#         coordinates = coordinates_list[current_index]
#         message = coordinates + "\n"  # Agregar salto de línea para el servidor
#         client_socket.sendall(message.encode('utf-8'))
#         print("Coordenadas enviadas:", coordinates)
        
#         # Actualizar el índice para la siguiente coordenada
#         current_index += 1

#         # Si se han enviado todas las coordenadas, enviar mensaje de "fin_gif"
#         if current_index >= len(coordinates_list):
#             client_socket.sendall("fin_gif\n".encode('utf-8'))
#             print("Se enviaron todas las coordenadas. Finalizando guardado del GIF.")
#             current_index = 0  # Reiniciar el índice si se quiere reiniciar el ciclo

#     elif option == "2":
#         # Enviar el comando de salida
#         client_socket.sendall("salir\n".encode('utf-8'))
#         print("Comando de salida enviado. Finalizando cliente...")
#         break
#     else:
#         print("Opción no válida. Intente nuevamente.")

# # Cerrar la conexión cuando el usuario decide salir
# client_socket.close()
