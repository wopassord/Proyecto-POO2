from datetime import datetime

class Archivo:

    def __init__(self, estado_conexion: bool, posicion, estado_actividad: str, ordenes=None):
        self.estado_conexion = estado_conexion  # Estado de la conexión (conectado/desconectado)
        self.posicion = posicion                  # Posición actual del robot
        self.estado_actividad = estado_actividad  # Estado de actividad actual
        self.tiempo = 0                      # Tiempo de actividad
        self.ordenes = ordenes if ordenes is not None else []  # Lista de órdenes ejecutadas
        self.cantidad_ordenes = len(self.ordenes)  # Cantidad de órdenes ejecutadas
        self.inicio_actividad = datetime.now() # Momento en que se inició la actividad

    def tiempo_transcurrido(self):
        """Calcula el tiempo de actividad en segundos."""
        ahora = datetime.now()
        tiempo_transcurrido = ahora - self.inicio_actividad
        self.tiempo = tiempo_transcurrido

    def mostrar_info(self):
        """Genera un reporte detallado de la actividad."""
        print("\n--- Reporte de Actividad ---")
        print("Estado de conexión:", self.estado_conexion)
        print("Posición del robot:", self.posicion)
        print("Estado de actividad:", self.estado_actividad)
        print("Inicio de la actividad:", self.inicio_actividad.strftime('%Y-%m-%d %H:%M:%S'))
        print("Tiempo de actividad:", self.tiempo)
        print("Ordenes:", self.ordenes)
        print("Cantidad de ordenes:", self.cantidad_ordenes)