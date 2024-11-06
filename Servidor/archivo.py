import csv

class Archivo:
    def __init__(self, estado_conexion=None, posicion="No Disponible", estado_actividad=None, ordenes=None):
        self.estado_conexion = estado_conexion
        self.posicion = posicion
        self.estado_actividad = estado_actividad
        self.inicio_actividad = None
        self.ordenes = ordenes if ordenes is not None else []
        self.cantidad_ordenes = 0
        self.ordenes_con_error = 0
        self.lista_ordenes_con_error = []
        self.inicios_sesion = [] 

    def cargar_datos_desde_ultimo_inicio(self, archivo_log='log_trabajo.csv'):
        """Carga los datos desde el último 'Inicio de actividad' en el log."""
        try:
            with open(archivo_log, mode='r') as csvfile:
                reader = csv.DictReader(csvfile)
                actividad_encontrada = False

                for row in reader:
                    if row['Peticiones'] == 'Inicio de actividad':
                        # Encontramos el inicio de una nueva actividad
                        actividad_encontrada = True
                        self.inicio_actividad = row['Fecha y Hora']
                        self.estado_conexion = True
                        self.ordenes = []
                        self.cantidad_ordenes = 0
                        self.ordenes_con_error = 0
                        self.lista_ordenes_con_error = []
                        self.inicios_sesion = []  

                    elif row['Peticiones'] == 'Iniciar Sesion' and actividad_encontrada:
                        # Agregamos el inicio de sesión con el usuario
                        self.inicios_sesion.append((row['Fecha y Hora'], row['Usuario']))

                    elif actividad_encontrada:
                        # Contamos las órdenes y las que tienen errores
                        self.ordenes.append(row['Peticiones'])
                        self.cantidad_ordenes += 1
                        if row['Fallos'] == '1':
                            self.ordenes_con_error += 1
                            self.lista_ordenes_con_error.append(row['Peticiones'])

        except FileNotFoundError:
            print(f"Error: El archivo '{archivo_log}' no se encuentra.")
        except Exception as e:
            print(f"Error al leer el archivo '{archivo_log}': {e}")

    def set_posicion_actual(self, respuesta):
        try:
            # Parsear la respuesta para extraer la posición
            if "ACTUAL POSITION" in respuesta:
                posicion = respuesta.split("[")[1].split("]")[0]
                self.posicion = f"[{posicion}]"
            else:
                self.posicion = "No disponible"
        except Exception as e:
            print(f"Error al procesar la posición del robot: {e}")
            self.posicion = "No disponible"

    def mostrar_info(self):
        """Genera un reporte detallado de la actividad desde el último inicio."""
        # Cargar los datos del log desde el último inicio de actividad
        self.cargar_datos_desde_ultimo_inicio()

        print("\n" + "=" * 40)
        print("REPORTE DE ACTIVIDAD DESDE EL ÚLTIMO INICIO")
        print("=" * 40)
        print(f"{'Estado de conexión:':<25} {'Conectado' if self.estado_conexion else 'Desconectado'}")
        print(f"{'Inicio de la actividad:':<25} {self.inicio_actividad}")
        print(f"{'Cantidad de órdenes:':<25} {self.cantidad_ordenes}")
        print(f"{'Órdenes con errores:':<25} {self.ordenes_con_error}")
        print(f"{'Posición actual del robot:':<25} {self.posicion}")

        # Mostrar inicios de sesión
        print("\nInicios de Sesión:")
        for i, (fecha, usuario) in enumerate(self.inicios_sesion, start=1):
            print(f"  {i}. {fecha} - Usuario: {usuario}")
            
        # Mostrar lista de órdenes
        print("\nLista de Órdenes Ejecutadas:")
        for i, orden in enumerate(self.ordenes, start=1):
            print(f"  {i}. {orden}")

        # Mostrar lista de órdenes con error, si existen
        if self.lista_ordenes_con_error:
            print("\nÓrdenes que tuvieron errores:")
            for i, orden in enumerate(self.lista_ordenes_con_error, start=1):
                print(f"  {i}. {orden}")
        else:
            print("\nNo hubo órdenes con errores.")

        print("=" * 40 + "\n")
