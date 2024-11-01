import xmlrpc.client

# Conexión al servidor
cliente = xmlrpc.client.ServerProxy("http://localhost:8080/")

def menu():
    print("\n--- Cliente de Pruebas para Arduino ---")
    print("1. Enviar comando al Arduino")
    print("2. Salir")
    return int(input("Seleccione una opción: "))

def main():
    while True:
        opcion = menu()
        if opcion == 1:
            comando = input("Ingrese el comando para el Arduino: ")
            try:
                # Llamar al servidor para enviar el comando
                respuesta = cliente.enviar_comando_arduino(comando)
                print("Respuesta del Arduino:", respuesta)
            except Exception as e:
                print("Error en la comunicación:", e)
        elif opcion == 2:
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    main()