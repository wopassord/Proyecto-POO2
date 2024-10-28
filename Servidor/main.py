from interfazServidor import InterfazServidor
from servidor import Servidor

def main():
    # Crear instancias de Servidor y pasarlo a InterfazServidor
    servidor = Servidor()
    interfaz = InterfazServidor(servidor, modo_trabajo="manual", modo_coordenadas="absolutas")

    # Iniciar el servidor y la interfaz de usuario en hilos separados
    servidor.iniciar_servidor()  
    interfaz.servidor.iniciar_interfaz()

    # Ejemplo de agregar usuario e iniciar sesión
    servidor.agregar_usuario("Renzito", "1234", True)
    servidor.iniciar_sesion()

    # Listar comandos y bucle principal
    interfaz.listar_comandos()
    ejecutando = True
    while ejecutando:
        try:
            opcion = int(input("Ingrese 0 si quiere salir, otro número para continuar: "))
            if opcion == 0:
                print("Saliendo del programa.")
                ejecutando = False
            else:
                interfaz.administrar_comandos()
        except ValueError:
            print("Por favor, ingresa un número válido.")

    # Apagar el servidor al salir
    if servidor.get_estado_servidor():
        servidor.apagar_servidor()
    print("Programa finalizado.")

if __name__ == "__main__":
    main()
