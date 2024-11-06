import numpy as np
import matplotlib.pyplot as plt
import re
from io import BytesIO
import os
from datetime import datetime



class SimuladorRobot:
    def __init__(self):
        self.movimientos = []  
        self.posicion_actual = np.array(
            [60, 0, 260]
        )  # Posición inicial del robot en el origen

    def procesar_gcode(self, contenido_gcode):
        """
        Lee y procesa el contenido de un archivo G-Code.
        Extrae los comandos G1 con coordenadas X, Y, Z para determinar las posiciones del robot.
        """
        for linea in contenido_gcode.splitlines():
            if linea.startswith("G1"):
                x, y, z = self.posicion_actual  # Valores por defecto

                match_x = re.search(r"X([-+]?\d*\.\d+|\d+)", linea)
                match_y = re.search(r"Y([-+]?\d*\.\d+|\d+)", linea)
                match_z = re.search(r"Z([-+]?\d*\.\d+|\d+)", linea)

                if match_x:
                    x = float(match_x.group(1))
                if match_y:
                    y = float(match_y.group(1))
                if match_z:
                    z = float(match_z.group(1))

                nueva_posicion = np.array([x, y, z], dtype=np.float64)

                # Agregar solo si la nueva posición es distinta de la posición actual
                if not np.array_equal(nueva_posicion, self.posicion_actual):
                    self.movimientos.append(nueva_posicion)
                    self.posicion_actual = nueva_posicion
                    print("Posición agregada:", nueva_posicion)  # Diagnóstico

    def visualizar_movimientos(self, returnBuffer=False):
        """
        Crea una visualización en 3D de los movimientos del robot y del modelo ABB IRB 460.
        """
        if not self.movimientos:
            print("No hay movimientos para visualizar.")
            return

        movimientos_array = np.array(self.movimientos)

        # Confirmar que movimientos_array tiene la forma esperada
        if movimientos_array.ndim != 2 or movimientos_array.shape[1] != 3:
            print("Error: movimientos_array no tiene la forma (n, 3).")
            print("movimientos_array:", movimientos_array)
            return

        # Figura para la trayectoria del robot
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection="3d")

        ax.plot(
            movimientos_array[:, 0],
            movimientos_array[:, 1],
            movimientos_array[:, 2],
            marker="o",
            color="b",
            label="Trayectoria",
        )

        # Representar articulaciones como vectores unitarios (versores)
        for i in range(1, len(movimientos_array)):
            origen = movimientos_array[i - 1]
            destino = movimientos_array[i]
            vector = destino - origen
            versor = vector / np.linalg.norm(vector)

            ax.quiver(
                origen[0],
                origen[1],
                origen[2],
                versor[0],
                versor[1],
                versor[2],
                length=1,
                color="r",
                normalize=True,
            )

        # Configuración de los ejes
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("Simulación de Movimientos del Robot")
        ax.legend()

        if returnBuffer:
            buffer = BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            return image_png

        plt.show(block=False)  # Modo no bloqueante

class UtilGcode:
    def __init__(self) -> None:
        pass
    def subir_archivo_gcode(
        self, nombre_archivo, contenido_archivo, returnBuffer=False
    ):
        """Guarda un archivo G-Code enviado por el cliente."""
        try:

            print("-------------------------------------------")
            print(f"Archivo {nombre_archivo} recibido.")
            print(f"Contenido del archivo: \n{contenido_archivo}")
            print("-------------------------------------------")

            simulador = SimuladorRobot()
            simulador.procesar_gcode(contenido_archivo)
            print("PROCESADO COMPLETAMENTE")
            if returnBuffer:
                buffer = simulador.visualizar_movimientos(True)
                if buffer is not None:
                    # Crear el directorio `./imagenes` si no existe
                    os.makedirs("Servidor/imagenes", exist_ok=True)

                    # Generar un nombre de archivo único para la imagen usando fecha y hora
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    image_path = f"{timestamp}_simulacion.png"
                    # Guardar la imagen en el path generado
                    with open(f"Servidor/imagenes/{image_path}", "wb") as img_file:
                        img_file.write(buffer)

                    return image_path  # Devolver el path de la imagen

            simulador.visualizar_movimientos(False)

            
            return f"Archivo {nombre_archivo} recibido y almacenado correctamente."

        except Exception as e:
            print(f"Error al guardar el archivo: {str(e)}")
            return None