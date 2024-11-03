from datetime import datetime
import csv
import Servidor

class LogTrabajo:
    def __init__(self, peticiones: str = None, usuario: str = None, fallos: int = 0, exitos: int = 0, tiempo_ejecucion: float = 0.0, IP: str = "127.0.0.1"):
        self.servidor = Servidor
        self.peticiones = peticiones
        self.IP = IP
        self.usuario = self.servidor.get_sesion().get('nombre_usuario', "Usuario desconocido")
        self.fallos = fallos
        self.exitos = exitos
        self.tiempo_ejecucion = tiempo_ejecucion
        self.escribir_CSV()

    def escribir_CSV(self, archivo='log_trabajo.csv'):
        "Escribe la información del log en un archivo CSV."
        # Generar la cabecera si el archivo no existe
        header = ['Fecha y Hora', 'Peticiones', 'IP', 'Usuario', 'Fallos', 'Exitos', 'Tiempo de Ejecucion']

        try:
            with open(archivo, mode='a', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Si el archivo está vacío, escribimos la cabecera
                if csvfile.tell() == 0:
                    writer.writerow(header)

                # Escribimos los datos del log
                writer.writerow([
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Fecha y hora actual
                    self.peticiones,
                    self.IP,
                    self.usuario,
                    self.fallos,
                    self.exitos,
                    self.tiempo_ejecucion
                ])

        except Exception as e:
            print(f"Error al escribir el log en {archivo}: {e}")

    def leer_CSV(self, archivo='log_trabajo.csv'):
        "Lee y muestra el contenido del archivo CSV."
        try:
            with open(archivo, mode='r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)  # Leer la cabecera
                print(" | ".join(header))  # Mostrar la cabecera con separadores

                for row in reader:
                    print(" | ".join(row))  # Mostrar cada fila de datos

        except FileNotFoundError:
            print(f"El archivo {archivo} no existe.")
        except Exception as e:
            print(f"Error al leer el archivo {archivo}: {e}")
