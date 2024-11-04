from datetime import datetime
import csv
from servidor import Servidor

class LogTrabajo:
    def __init__(self, servidor:Servidor, peticion: int = 0, usuario: str = None, fallos: int = 0, exitos: int = 0, tiempo_ejecucion: float = 0.0, IP: str = "127.0.0.1"):
        self.servidor = servidor
        self.peticion = peticion
        self.IP = IP
        self.usuario = self.servidor.get_sesion().get('nombre_usuario', "Usuario desconocido")
        self.fallos = fallos
        self.exitos = exitos
        self.tiempo_ejecucion = float(tiempo_ejecucion)

    def actualizar_log(self, peticion=None, usuario=None, fallos=0, exitos=0, tiempo_ejecucion=0.0, IP="127.0.0.1"):
        """Actualizar los atributos del log sin escribir en el CSV inmediatamente."""
        if peticion:
            self.peticion = peticion
        if usuario:
            self.usuario = usuario
        self.fallos = fallos
        self.exitos = exitos
        self.tiempo_ejecucion = float(tiempo_ejecucion)
        self.IP = IP

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
                    self.peticion,
                    self.IP,
                    self.usuario,
                    self.fallos,
                    self.exitos,
                    self.tiempo_ejecucion
                ])

        except Exception as e:
            print(f"Error al escribir el log en {archivo}: {e}")

    def leer_CSV(self, archivo='log_trabajo.csv'):
        """Leer y mostrar el contenido del archivo CSV de manera alineada."""
        try:
            with open(archivo, mode='r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                
                # Leer y almacenar todas las filas
                rows = list(reader)
                
                # Definir los anchos de columna
                col_widths = [20, 45, 15, 20, 10, 10, 20]  # Puedes ajustar los valores según sea necesario
                
                num_rows_to_show = min(len(rows) - 1, 100)
                # Imprimir cabecera alineada
                header = rows[0]
                for i, col in enumerate(header):
                    print(col.ljust(col_widths[i]), end=" | ")
                print("\n" + "-" * (sum(col_widths) + len(col_widths) * 3))

                rows_to_display = rows[-num_rows_to_show:]

                # Imprimir cada fila de datos alineada
                for row in rows_to_display:
                    for i, col in enumerate(row):
                        # Convertir el tiempo de ejecución a milisegundos con formato adecuado
                        if i == 6:  # Índice de la columna de tiempo de ejecución
                            tiempo_ms = f"{float(col):.2f} ms"
                            print(tiempo_ms.ljust(col_widths[i]), end=" | ")
                        else:
                            print(col.ljust(col_widths[i]), end=" | ")
                    print()

        except FileNotFoundError:
            print(f"El archivo {archivo} no existe.")
        except Exception as e:
            print(f"Error al leer el archivo {archivo}: {e}")


    def leer_CSV_aux(self, archivo='log_trabajo.csv'): ##ESTA RECORRE EL CSV SOLAMENTE PARA VERIFICAR ERRORES (EXITO/FALLOS)
        """Leer y mostrar el contenido del archivo CSV de manera alineada."""
        try:
            with open(archivo, mode='r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                
                # Leer y almacenar todas las filas
                rows = list(reader)
                
                # Definir los anchos de columna
                col_widths = [20, 45, 15, 20, 10, 10, 20]  # Puedes ajustar los valores según sea necesario
                
                num_rows_to_show = min(len(rows) - 1, 100)
                # Imprimir cabecera alineada
                header = rows[0]
                # for i, col in enumerate(header):
                #     print(col.ljust(col_widths[i]), end=" | ")
                # print("\n" + "-" * (sum(col_widths) + len(col_widths) * 3))

                rows_to_display = rows[-num_rows_to_show:]

                # Imprimir cada fila de datos alineada
                # for row in rows_to_display:
                #     for i, col in enumerate(row):
                #         # Convertir el tiempo de ejecución a milisegundos con formato adecuado
                #         if i == 6:  # Índice de la columna de tiempo de ejecución
                #             tiempo_ms = f"{float(col):.2f} ms"
                #             print(tiempo_ms.ljust(col_widths[i]), end=" | ")
                #         else:
                #             print(col.ljust(col_widths[i]), end=" | ")
                #     print()

        except FileNotFoundError:
            print(f"El archivo {archivo} no existe.")
        except Exception as e:
            print(f"Error al leer el archivo {archivo}: {e}")
