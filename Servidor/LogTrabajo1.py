from datetime import datetime
import csv

class LogTrabajo:
    def __init__(self, servidor=None, peticion=0, usuario=None, fallos=0, exitos=0, tiempo_ejecucion=0.0, IP="127.0.0.1",):
        self.servidor = servidor
        self.peticion = peticion
        self.IP = IP
        self.usuario = usuario if usuario else "Usuario desconocido"
        self.fallos = fallos
        self.exitos = exitos
        self.tiempo_ejecucion = float(tiempo_ejecucion)

    def actualizar_log(self, peticion=None, usuario=None, fallos=0, exitos=0, tiempo_ejecucion=0.0, IP="127.0.0.1",):
        """Actualizar los atributos del log sin escribir en el CSV inmediatamente."""
        if peticion:
            self.peticion = peticion
        if usuario:
            self.usuario = usuario
        self.fallos = fallos
        self.exitos = exitos
        self.tiempo_ejecucion = float(tiempo_ejecucion)
        self.IP = IP

    def escribir_CSV(self, archivo="log_trabajo.csv"):
        "Escribe la información del log en un archivo CSV."
        header = ["Fecha y Hora","Peticiones","IP","Usuario","Fallos","Exitos","Tiempo de Ejecucion",]

        try:
            with open(archivo, mode="a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                if csvfile.tell() == 0:
                    writer.writerow(header)
                writer.writerow(
                    [datetime.now().strftime("%Y-%m-%d %H:%M:%S"),self.peticion,self.IP,self.usuario,self.fallos,self.exitos,self.tiempo_ejecucion,]
                )

        except Exception as e:
            print(f"Error al escribir el log en {archivo}: {e}")

    def leer_CSV(self, archivo="log_trabajo.csv"):
        """Leer y mostrar el contenido del archivo CSV de manera alineada."""
        try:
            with open(archivo, mode="r", newline="") as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)
                col_widths = [20,55,10,9,8,8,21,]  

                num_rows_to_show = min(len(rows) - 1, 100)
                header = rows[0]
                for i, col in enumerate(header):
                    print(col.ljust(col_widths[i]), end=" | ")
                print("\n" + "-" * (sum(col_widths) + len(col_widths) * 3))

                rows_to_display = rows[-num_rows_to_show:]

                for row in rows_to_display:
                    for i, col in enumerate(row):
                        if i == 6:
                            tiempo_ms = f"{float(col):.2f} ms"
                            print(tiempo_ms.ljust(col_widths[i]), end=" | ")
                        else:
                            print(col.ljust(col_widths[i]), end=" | ")
                    print()

        except FileNotFoundError:
            print(f"El archivo {archivo} no existe.")
        except Exception as e:
            print(f"Error al leer el archivo {archivo}: {e}")
