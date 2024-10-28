
from interfazServidor import InterfazServidor

def main():
    # Crear una instancia de InterfazServidor
    interfaz = InterfazServidor(modo_trabajo="manual", modo_coordenadas="absolutas")

    interfaz.servidor.agregar_usuario("Renzito", "1234", True)
    interfaz.servidor.iniciar_sesion()

    interfaz.listar_comandos()

    # Bucle principal del programa para administrar comandos
    ejecutando = True
    while ejecutando:
        
        try:
            opcion = int(input("Ingrese 0 si quiere salir, si no, imprima cualquier otro numero: "))
            if opcion == 0:
                print("Saliendo del programa.")
                ejecutando = False
            else:
                interfaz.administrar_comandos()
        except ValueError:
            print("Por favor, ingresa un número válido.")

    # Apagar el servidor antes de salir
    if interfaz.servidor.get_estado_servidor():
        interfaz.servidor.apagar_servidor()
    print("Programa finalizado.")

if __name__ == "__main__":
    main()