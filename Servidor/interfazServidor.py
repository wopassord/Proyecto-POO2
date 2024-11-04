from archivo import Archivo
from logTrabajo import LogTrabajo
from controlador import Controlador
import time

class InterfazServidor:
    def __init__(self, servidor, modo_trabajo="automatico", modo_coordenadas="absolutas"):
        self.servidor = servidor  # Instancia del Servidor
        self.modo_trabajo = modo_trabajo
        self.controlador = Controlador()  # Instancia de Controlador
        self.modo_coordenadas = modo_coordenadas
        self.usuario = None
        self.peticion = None
        self.ip_cliente = "127.0.0.1"
        self.log_trabajo = LogTrabajo(servidor=servidor)
        self.fallos = 0
        self.exitos = 0
        self.archivo = Archivo(estado_conexion=self.servidor.get_estado_servidor(),
                        posicion="Inicio", estado_actividad="Inactiva")

    def registrar_log_csv(self, peticion, fallos=0, exitos=1, tiempo_ejecucion=0.0, IP="127.0.01"):
        sesion = self.servidor.get_sesion()
        usuario = sesion.get('nombre_usuario', "Usuario desconocido") if sesion else "Usuario desconocido"
        # Actualizar el log sin escribir en el archivo
        self.log_trabajo.actualizar_log(peticion=peticion, usuario=usuario, fallos=fallos, exitos=exitos, tiempo_ejecucion=tiempo_ejecucion, IP=self.ip_cliente)
        # Guardar en el archivo CSV
        self.log_trabajo.escribir_CSV()

    def listar_comandos(self):
        print("Comandos posibles a realizar: \n")
        print(" 1) Conectar/desconectar robot.")
        print(" 2) Activar/desactivar motores del robot.")
        print(" 3) Seleccionar los modos de trabajo (manual o automatico).")
        print(" 4) Seleccionar los modos de coordenadas (absolutas o relativas).")
        print(" 5) Mostrar operaciones posibles a realizar por un cliente o un operador en el servidor.")
        print(" 6) [SOLO MODO MANUAL] Enviar comandos en formato G-Code para accionar robot.")
        print(" 7) [MODO AUTOMÁTICO] Cargar y ejecutar un archivo en formado G-Code.")
        print(" 8) Mostrar reporte de informacion general.")
        print(" 9) [SOLO ADMIN] Mostrar reporte de log de trabajo del servidor.")
        print(" 10) [SOLO ADMIN] Mostrar usuarios.")
        print(" 11) [SOLO ADMIN] Mostrar/editar los parametros de conexion del robot.")
        print(" 12) [SOLO ADMIN] Encender/apagar servidor.")
        print(" 13) Cerrar sesion.")
        print(" 14) Listar comandos nuevamente.")
        print(" 15) Apagar programa.")
        exito = 1
        self.exitos = exito


    def recibir_comando_cliente(self, comando):
        # Recibe un comando desde el servidor (que lo recibe de cliente) y lo procesa.
        if comando not in list(range(1, 5)):
            respuesta = self.controlador.enviar_comando(comando)
        else:
            respuesta = self.administrar_comandos(comando)
        return respuesta

    def administrar_comandos(self, opcion_elegida = None):
        while True:
            try:
                if opcion_elegida is None:
                    # Caso normal: se pide alguna accion desde el servidor
                    opcion_elegida = int(input("Ingrese la acción a realizar: "))
                    respuesta = self.ejecucion_administrar_comando(opcion_elegida)
                    break
                else:
                    # Caso particular: se pide alguna accion desde el cliente
                    self.peticion=opcion_elegida    #Esto se hace para almacenar en el log de trabajo
                    print(f"ACCION REALIZADA POR CLIENTE CON IP: {self.ip_cliente}")
                    respuesta = self.ejecucion_administrar_comando(opcion_elegida)   
                    break
            except ValueError:
                print("Por favor, ingrese un número válido.")
            opcion_elegida = None
        return respuesta

    def ejecucion_administrar_comando(self, opcion_elegida):
        # Inicializar la variable 'respuesta' para evitar errores
        respuesta = None
        # Ejecución de opciones
        respuesta = None
        inicio = time.time()
        if opcion_elegida == 1:
            self.peticion = "Activar/desactivar robot"
            respuesta = self.activar_desactivar_robot()
            # Espera a mensaje inicial
            time.sleep(1.5)
        elif opcion_elegida == 2:
            self.peticion = "Activar/desactivar motores"
            respuesta = self.activar_desactivar_motores()
        elif opcion_elegida == 3:
            self.peticion = "Seleccionar modo de trabajo"
            respuesta = self.seleccionar_modo_trabajo()
        elif opcion_elegida == 4:
            self.peticion = "Seleccionar modo de coordenadas"
            respuesta = self.seleccionar_modo_coordenadas()
        elif opcion_elegida == 5:
            self.peticion = "Mostrar operaciones cliente"
            self.mostrar_operaciones_cliente()
            respuesta = "Operaciones mostradas."
        elif opcion_elegida == 6:
            self.peticion = "Escribir comando"
            self.escribir_comando()
            respuesta = "Comando escrito en modo manual."
        elif opcion_elegida == 7:
            self.peticion = "Cargar y ejecutar archivo G-Code."
            respuesta = self.cargar_y_ejecutar_archivo_gcode()
        elif opcion_elegida == 8:
            self.peticion = "Mostrar reporte general"
            self.mostrar_reporte_general()
            respuesta = "Resporte general mostrado."
        elif opcion_elegida == 9:
            self.peticion = "Mostrar log de trabajo"
            duracion = (time.time() - inicio)*1000  # Calcular el tiempo de ejecución
            self.mostrar_log_trabajo_aux()
            self.registrar_log_csv(peticion=self.peticion,fallos=self.fallos , exitos=self.exitos,tiempo_ejecucion=duracion,IP=self.ip_cliente)
            self.mostrar_log_trabajo()
            respuesta = "Log de trabajo mostrado."
        elif opcion_elegida == 10:
            self.peticion = "Mostrar usuarios"
            self.mostrar_usuarios()
            respuesta = "Usuarios mostrados."
        elif opcion_elegida == 11:
            self.peticion = "Modificar parámetros de conexión"
            self.modificar_parametros_conexion()
            respuesta = "Parámetros de conexión modificados."
        elif opcion_elegida == 12:
            self.peticion = "Encender/apagar servidor"
            if not self.servidor.get_estado_servidor():
                exito = self.servidor.iniciar_servidor()
                respuesta = "Servidor iniciado."
                self.exitos = exito
                self.fallos= 1 - exito
            else:
                exito = self.servidor.apagar_servidor()
                respuesta = "Servidor apagado."
                self.exitos = exito
                self.fallos = 1 - exito
        elif opcion_elegida == 13:
            self.peticion = "Cerrar sesión"
            duracion = (time.time() - inicio)*1000  # Calcular el tiempo de ejecución
            exito = 1
            self.exitos = exito
            self.fallos = 1 - exito
            self.registrar_log_csv(peticion=self.peticion,fallos=self.fallos, exitos=self.exitos, tiempo_ejecucion=duracion,IP=self.ip_cliente)
            self.servidor.cerrar_sesion()
            respuesta = "Sesión cerrada."
        elif opcion_elegida == 14:
            self.peticion = "Listar comandos nuevamente"
            self.listar_comandos()
            respuesta = "Comandos listados nuevamente."
        elif opcion_elegida == 15:
            self.peticion = "Apagar programa"
            duracion = (time.time() - inicio)*1000  # Calcular el tiempo de ejecución
            exito=1
            self.exitos=exito
            self.fallos=1-exito
            self.registrar_log_csv(peticion=self.peticion,fallos=self.fallos, exitos=self.exitos, tiempo_ejecucion=duracion,IP=self.ip_cliente)
            return 15
        else:
            print("Opción no válida.")
            respuesta = "Opción inválida."
        
        if opcion_elegida not in [9, 15, 13]:
            duracion = (time.time() - inicio)*1000  # Calcular el tiempo de ejecución
            self.registrar_log_csv(peticion=self.peticion,fallos=self.fallos, exitos=self.exitos, tiempo_ejecucion=duracion,IP=self.ip_cliente)
            # logtrabajo = LogTrabajo(servidor=self.servidor,peticion=self.peticion,exitos=1 if respuesta != "Opción inválida" else 0,tiempo_ejecucion=duracion,IP=self.ip_cliente)
    
        return respuesta

    # Métodos adicionales para manipular el robot y mostrar reportes
    def activar_desactivar_robot(self):
        if not self.controlador.get_estado_robot():  # Solo conectar si está desconectado
            respuesta, exito = self.controlador.conectar_robot()
            self.peticion = "Conectar robot"
            self.exitos = exito
            self.fallos = 1 - exito
        else:
            respuesta, exito = self.controlador.desconectar_robot()
            self.peticion = "Desconectar robot"
            self.exitos = exito
            self.fallos = 1 - exito
        return respuesta

    def activar_desactivar_motores(self):
        if self.controlador.get_estado_motores():
            respuesta, exito = self.controlador.desactivar_motores()  # Usamos la instancia
            self.peticion = "Desactivar motores"
        else:
            respuesta, exito = self.controlador.activar_motores()
            self.peticion = "Activar motores"

        self.exitos = exito
        self.fallos = 1 - exito
        return respuesta

    def mostrar_reporte_general(self):
        try:
            Archivo.mostrar_info()  # Muestra información general
            self.peticion = "Mostrar reporte general"
            exito = 1
            self.exitos = exito
            self.fallos = 1 - exito
        except FileNotFoundError:
            exito = 0
            self.exitos = exito
            self.fallos = 1 - exito
            print("Error: No se encontró el archivo requerido para mostrar el reporte general.")
        except IOError:
            exito = 0
            self.exitos = exito
            self.fallos = 1 - exito
            print("Error: Hubo un problema al leer el archivo para el reporte general.")
        except Exception as e:
            exito = 0
            self.exitos = exito
            self.fallos = 1 - exito
            print(f"Error inesperado: {e}")

    def mostrar_log_trabajo(self):
        self.peticion = "Mostrar log de trabajo"
        if self.verificar_sesion_admin() == True:
            try:
                self.log_trabajo.leer_CSV() 
                exito = 1
                self.exitos = exito
                self.fallos = 1 - exito
            except FileNotFoundError:
                print("Error: El archivo de log de trabajo no se encuentra.")
                exito = 0
                self.exitos = exito
                self.fallos = 1 - exito
            except PermissionError:
                print("Error: Permisos insuficientes para acceder al archivo de log de trabajo.")
                exito = 0
                self.exitos = exito
                self.fallos = 1 - exito
            except Exception as e:
                print(f"Error inesperado: {e}")
                exito = 0
                self.exitos = exito
                self.fallos = 1 - exito
        else:
            exito = 0
            self.exitos = exito
            self.fallos = 1 - exito 
            
    def seleccionar_modo_trabajo(self):
        if self.modo_trabajo == "manual":
            self.modo_trabajo = "automatico"
            self.peticion = "Seleccionar modo automatico"
            exito = 1
            self.exitos = exito
            self.fallos = 1 - exito
        elif self.modo_trabajo == "automatico":
            self.modo_trabajo = "manual"
            self.peticion = "Seleccionado modo manual"
            exito = 1
            self.exitos = exito
            self.fallos = 1 - exito
        respuesta = f"Modo de trabajo seleccionado: {self.modo_trabajo}"
        print(respuesta)
        return respuesta

    def seleccionar_modo_coordenadas(self):
        if self.modo_coordenadas == "absolutas":
            self.modo_coordenadas = "relativas"
            respuesta, exito = self.controlador.enviar_comando('G91')
            self.peticion = "Seleccionar modo de coordenadas relativas"
            self.exitos = exito
            self.fallos = 1 - exito
        elif self.modo_coordenadas == "relativas":
            self.modo_coordenadas = "absolutas"
            respuesta, exito = self.controlador.enviar_comando('G90')
            self.peticion = "Seleccionar modo de coordenadas absolutas"
            self.exitos = exito
            self.fallos = 1 - exito
        return respuesta

    def mostrar_usuarios(self):
        self.peticion = "Mostrar usuarios"
        if self.verificar_sesion_admin() == True:
            exito = 1
            self.exitos = exito
            self.fallos = 1 - exito
            for u in self.usuarios:
                print(u.nombre_usuario)  # Muestra el nombre del usuario
            return


    def modificar_parametros_conexion(self):
        self.peticion = "Modificar parametros de conexion"
        if self.verificar_sesion_admin() == True:
            try:
                puerto_COM = input('Ingrese el nuevo puerto de COM al que se quiere conectar: ')
                baudrate = int(input('Ingrese la velocidad de comunicacion (baudrate): '))
                self.controlador.cambiar_parametros_comunicacion(baudrate, puerto_COM)
                self.controlador.conectar_robot()
                exito = 1
                self.exitos = exito 
                self.fallos = 1 - exito
    
            except Exception as e:
                print(f"Error al modificar los parámetros de conexión: {e}")
                exito = 1
                self.exitos = exito 
                self.fallos = 1 - exito 
                

    def mostrar_operaciones_cliente(self):
        print("\nOperaciones posibles a realizar por un cliente o por un operador en el servidor: \n")
        print("M3: Activar gripper.")
        print("M5: Desactivar gripper.")
        print("G28: Hacer homing.")
        print("G1: Hacer un movimiento a una determinada posición (para enviar este comando, realizar lo siguiente: [G1 Xa Yb Zc], donde Xa, Yb y Zc son las posiciones a las que se debe mover).")
        print("M114: Reporte de modo de coordenadas y posición actual.")
        print("G90: Modo de coordenadas absolutas.")
        print("G91: Modo de coordenadas relativas.")
        print("M17: Activar motores.")
        print("M18: Desactivar motores.\n")
        exito = 1
        self.exitos = exito
        self.fallos = 1 - exito
    

    def escribir_comando(self):
        # #self.peticion = "Enviar comando"
        if self.modo_trabajo == "manual":
            try: 
                comando = input("Ingrese el comando en G-Code para accionar el robot: ")
                respuesta, exito = self.controlador.enviar_comando(comando)
                self.exitos = exito
                self.fallos = 1 - exito
            except Exception as e:
                print(f"Error al enviar el comando: {e} ")
                exito = 0
                self.exitos = exito
                self.fallos = 1 - exito
        else: 
            print("El modo de trabajo no es manual. Por favor, cambie el modo de trabajo antes de realizar esta accion.")
            exito = 0
            self.exitos = exito
            self.fallos = 1 - exito

    def verificar_sesion_admin(self):
        self.sesion = self.servidor.get_sesion()
        self.usuarios = self.servidor.get_usuarios()

        if self.sesion and 'nombre_usuario' in self.sesion:
                nombre_usuario = self.sesion['nombre_usuario']
                
                # Verificamos si el usuario tiene permisos de administrador
                for usuario in self.usuarios:
                    if usuario.nombre_usuario == nombre_usuario and usuario.admin:
                        # Seguir la funcion si el usuario tiene permisos de administrador
                        return True
    
                print("Acceso denegado. Solo los administradores pueden realizar esta accion")
                exito = 0
                self.exitos = exito
                self.fallos = 1 - exito
                return False
        
        else:
            print("No hay ningún usuario en sesión.")
            return False
        
    def cargar_y_ejecutar_archivo_gcode(self):

        if self.modo_trabajo != "automatico":
            print("Esta acción solo está disponible en modo automático. Cambie el modo de trabajo a automático para proceder.")
            return
        nombre_archivo = input("Ingrese el nombre del archivo G-Code a cargar (con extensión): ")
        try:
            with open(nombre_archivo, 'r', encoding='latin-1') as archivo:
                print(f"Ejecutando comandos en {nombre_archivo}...")
                for linea in archivo:
                    comando = linea.split(";")[0].strip()
                    if comando:
                        respuesta, exito = self.controlador.enviar_comando(comando)
                        if exito == 0:
                            print(f"Error al ejecutar comando: {respuesta}")
                            break
                        time.sleep(0.5)
                print(f"Archivo {nombre_archivo} ejecutado correctamente.")
                exito = 1 

        except FileNotFoundError:
            print(f"Error: No se pudo encontrar el archivo {nombre_archivo}. Verifique la ruta y el nombre.")
            exito = 0

        except Exception as e:
            print(f"Error al ejecutar el archivo: {e}")
            exito = 0
        
        self.exitos = exito
        self.fallos = 1 - exito

    def verificar_sesion_admin_aux(self): ##SOLO PARA VERIFICAR ERRORES EN EL EXITOS/FALLOS DE MOSTRAR LOG
        self.sesion = self.servidor.get_sesion()
        self.usuarios = self.servidor.get_usuarios()

        if self.sesion and 'nombre_usuario' in self.sesion:
                nombre_usuario = self.sesion['nombre_usuario']
                
                # Verificamos si el usuario tiene permisos de administrador
                for usuario in self.usuarios:
                    if usuario.nombre_usuario == nombre_usuario and usuario.admin:
                        # Seguir la funcion si el usuario tiene permisos de administrador
                        return True

                exito = 0
                self.exitos = exito
                self.fallos = 1 - exito
                return False
        
        else:
            return False
    def mostrar_log_trabajo_aux(self): ##ESTA SOLO RECORRE SIN PRINTEAR NADA PARA VERIFICAR ERRORES UNICAMENTE
        self.peticion = "Mostrar log de trabajo"
        if self.verificar_sesion_admin_aux() == True:
            try:
                self.log_trabajo.leer_CSV_aux() 
                exito = 1
                self.exitos = exito
                self.fallos = 1 - exito
            except FileNotFoundError:
                print("Error: El archivo de log de trabajo no se encuentra.")
                exito = 0
                self.exitos = exito
                self.fallos = 1 - exito
            except PermissionError:
                print("Error: Permisos insuficientes para acceder al archivo de log de trabajo.")
                exito = 0
                self.exitos = exito
                self.fallos = 1 - exito
            except Exception as e:
                print(f"Error inesperado: {e}")
                exito = 0
                self.exitos = exito
                self.fallos = 1 - exito
        else:
            exito = 0
            self.exitos = exito
            self.fallos = 1 - exito 
