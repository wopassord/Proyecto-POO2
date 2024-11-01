from interfazServidor import InterfazServidor
from servidor import Servidor

def main():
    # Crear instancias de Servidor y pasarlo a InterfazServidor
    servidor = Servidor()
    interfaz = InterfazServidor(servidor, modo_trabajo="manual", modo_coordenadas="absolutas")

    # Iniciar el servidor y la interfaz de usuario en hilos separados
    servidor.iniciar_servidor()  
    interfaz.servidor.iniciar_interfaz()

    # Leer usuarios disponibles
    servidor.leer_usuarios_csv()


    ejecutando = True
    while ejecutando:
        if not servidor.sesion_iniciada:
            try:
                print("Inicie sesion antes de proceder.")
                print(" 1) Iniciar sesion")
                print(" 2) Agregar usuario")
                opcion = int(input("Por favor, ingrese una de las anteriores opciones: \n"))
                if opcion == 1:
                    servidor.iniciar_sesion()
                    if servidor.sesion_iniciada:
                        interfaz.listar_comandos()
                elif opcion == 2:
                     # Pedir datos del usuario para agregar
                    nombre_usuario = input("Ingrese el nombre de usuario: ")
                    contrasena = input("Ingrese la contraseña: ")
                    servidor.agregar_usuario(nombre_usuario, contrasena)
            except ValueError:
                print("Ingrese un numero valido.")
        else:
            try:
                comando = interfaz.administrar_comandos()
                if comando == 14:
                    ejecutando = False
            except ValueError:
                print("Por favor, ingresa un número válido.")

    # Apagar el servidor al salir
    if servidor.get_estado_servidor():
        servidor.apagar_servidor()
    print("Programa finalizado.")

if __name__ == "__main__":
    main()
