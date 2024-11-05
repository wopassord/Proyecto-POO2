from interfazServidor import InterfazServidor
from servidor import Servidor
import time
from servidor import Servidor
from servidor_http import app
import threading
import uvicorn


def init_rpc_server():
    # Crear instancias de Servidor y pasarlo a InterfazServidor
    servidor = Servidor()
    interfaz = InterfazServidor(
        servidor, modo_trabajo="manual", modo_coordenadas="absolutas"
    )

    # Registrar el inicio de sesión en el log (indica el inicio de la actividad)
    interfaz.registrar_inicio_sesion()  # Nueva llamada aquí para registrar el inicio
    
    # Iniciar el servidor y la interfaz de usuario en hilos separados
    servidor.asignar_interfaz(interfaz) 


    # Leer usuarios disponibles
    servidor.leer_usuarios_csv()

    # Para que los mensajes se vean bien
    time.sleep(1)

    # Se inicia el programa
    ejecutando = True
    try:
        while ejecutando:
            # Se inicia sesion en un principio
            if not servidor.sesion_iniciada:
                try:
                    # Muestra el menu de opciones. Se inicia sesion, o se agrega un usuario para esto
                    print("Inicie sesion antes de proceder.")
                    print(" 1) Iniciar sesion")
                    print(" 2) Agregar usuario")
                    opcion = int(
                        input("Por favor, ingrese una de las anteriores opciones: \n")
                    )
                    # Inicio de sesion
                    if opcion == 1:
                        servidor.iniciar_sesion()
                        if servidor.sesion_iniciada:
                            interfaz.registrar_log_csv(peticion="Iniciar Sesion",fallos=0, exitos=1, tiempo_ejecucion=0,IP=servidor.ip_cliente)
                            servidor.iniciar_servidor()
                            interfaz.listar_comandos()
                    # Se agrega un usuario
                    elif opcion == 2:
                        # Pedir datos del usuario para agregar
                        nombre_usuario = input("Ingrese el nombre de usuario: ")
                        contrasena = input("Ingrese la contraseña: ")
                        servidor.agregar_usuario(nombre_usuario, contrasena)
                except ValueError:
                    print("Ingrese un numero valido.")
            else:
                try:
                    # Si el arduino esta conectado, verificamos si hay alguna respuesta de este
                    if interfaz.controlador.get_estado_robot():
                        # Si hay respuestas, va a mandarlas todas antes de poder realizar alguna accion
                        interfaz.controlador.procesar_respuestas_arduino()
                    # Se permite ingresar una accion en consola para realizar acciones en la interfaz
                    comando = interfaz.administrar_comandos()
                    if comando == 15:  # Comando para salir del programa
                        ejecutando = False
                except ValueError:
                    print("Por favor, ingresa un número válido.")
    finally:
        # Apagar el servidor al salir
        if servidor.get_estado_servidor():
            servidor.apagar_servidor()
        if interfaz.controlador.get_estado_robot():
            interfaz.controlador.desconectar_robot()
        if hasattr(interfaz, 'archivo_trayectoria'):
            interfaz.archivo_trayectoria.close()
        print("Programa finalizado.")


if __name__ == "__main__":
    init_rpc_server()
