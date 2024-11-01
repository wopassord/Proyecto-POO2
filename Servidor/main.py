from interfazServidor import InterfazServidor
from servidor import Servidor

def main():
    # Crear instancia del servidor y de la interfaz
    servidor = Servidor()
    interfaz = InterfazServidor(servidor, modo_trabajo="manual", modo_coordenadas="absolutas")
    servidor.asignar_interfaz(interfaz)  # Asignar la interfaz al servidor

    # Iniciar el servidor y la interfaz en hilos separados
    servidor.iniciar_servidor()
    servidor.iniciar_interfaz()  # Ya tienes acceso directo a la interfaz desde el servidor

    en_ejecucion = True
    while en_ejecucion:
        if not servidor.sesion_iniciada:
            opcion = menu_principal()
            if opcion == 1:
                servidor.iniciar_sesion()
                if servidor.sesion_iniciada:
                    interfaz.listar_comandos()
            elif opcion == 2:
                agregar_usuario(servidor)
        else:
            comando = interfaz.administrar_comandos()
            if comando == 14:  # Comando para salir
                en_ejecucion = False

    # Apagar el servidor XML-RPC y finalizar el programa
    if servidor.get_estado_servidor():
        servidor.apagar_servidor()
    print("Programa finalizado.")

def menu_principal():
    """Muestra el menú principal y devuelve la opción elegida."""
    while True:
        try:
            print("Inicie sesión antes de proceder.")
            print(" 1) Iniciar sesión")
            print(" 2) Agregar usuario")
            opcion = int(input("Por favor, ingrese una de las anteriores opciones: \n"))
            if opcion in (1, 2):
                return opcion
        except ValueError:
            print("Ingrese un número válido.")

def agregar_usuario(servidor):
    """Función para agregar un usuario al sistema."""
    nombre_usuario = input("Ingrese el nombre de usuario: ")
    contrasena = input("Ingrese la contraseña: ")
    servidor.agregar_usuario(nombre_usuario, contrasena)

if __name__ == "__main__":
    main()
