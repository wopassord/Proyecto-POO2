from xmlrpc.server import SimpleXMLRPCServer
import serial
import time

# Configurar el puerto serial (ajustar según el puerto usado por tu Arduino)
puerto_serie = 'COM10'  # Cambiar a '/dev/ttyUSB0' en Linux
velocidad_baudios = 115200

try:
    arduino = serial.Serial(puerto_serie, velocidad_baudios, timeout=1)
    print(f"Conectado al Arduino en {puerto_serie} a {velocidad_baudios} baudios.")
except Exception as e:
    print(f"No se pudo conectar al Arduino: {e}")
    exit()

# Definir el servidor XML-RPC
servidor = SimpleXMLRPCServer(("localhost", 8080), allow_none=True)
print("Servidor XML-RPC en espera en el puerto 8080...")

def enviar_comando_arduino(comando):
    """
    Envía un comando al Arduino y devuelve la respuesta.
    """
    try:
        # Enviar comando al Arduino
        arduino.write((comando + '\n').encode())
        time.sleep(0.1)  # Pequeña espera para que el Arduino procese el comando

        # Leer respuesta del Arduino
        respuesta = arduino.readline().decode().strip()
        return respuesta
    except Exception as e:
        return f"Error en la comunicación con Arduino: {e}"

# Registrar el método de envío de comandos
servidor.register_function(enviar_comando_arduino, "enviar_comando_arduino")

# Iniciar el servidor
try:
    servidor.serve_forever()
except KeyboardInterrupt:
    print("Servidor detenido.")
finally:
    arduino.close()