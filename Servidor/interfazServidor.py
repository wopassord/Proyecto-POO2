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
        self.ip_cliente = None

    def listar_comandos(self):
        print("Comandos posibles a realizar: \n")
        print(" 1) Conectar/desconectar robot.")
        print(" 2) Activar/desactivar motores del robot.")
        print(" 3) Seleccionar los modos de trabajo (manual o automatico)")
        print(" 4) Seleccionar los modos de coordenadas (absolutas o relativas)")
        print(" 5) Mostrar operaciones posibles a realizar por un cliente o un operador en el servidor.")
        print(" 6) [SOLO MODO MANUAL] Enviar comandos en formato G-Code para accionar robot.")
        print(" 7) Mostrar reporte de informacion general.")
        print(" 8) [SOLO ADMIN] Mostrar reporte de log de trabajo del servidor.")
        print(" 9) [SOLO ADMIN] Mostrar usuarios.")
        print(" 10) [SOLO ADMIN] Mostrar/editar los parametros de conexion del robot.")
        print(" 11) [SOLO ADMIN] Encender/apagar servidor.")
        print(" 12) Cerrar sesion.")
        print(" 13) Listar comandos nuevamente.")
        print(" 14) Apagar programa.")

    def administrar_comandos(self, opcion_elegida = None):
        while True:
            try:
                if opcion_elegida == None:
                    # Caso normal: se pide alguna accion desde el servidor
                    opcion_elegida = int(input("Ingrese la acción a realizar: "))
                    self.ejecucion_administrar_comando(opcion_elegida)
                else:
                    # Caso particular: se pide alguna accion desde el cliente
                    print(f"ACCION REALIZADA POR CLIENTE CON IP: {self.ip_cliente}")
                    respuesta = self.ejecucion_administrar_comando(opcion_elegida)
                    opcion_elegida = None
                    return respuesta    
            except ValueError:
                print("Por favor, ingrese un número válido.")
                opcion_elegida = None

    def ejecucion_administrar_comando(self, opcion_elegida):
        # Ejecución de opciones
        inicio = time.time()
        if opcion_elegida == 1:
            respuesta = self.activar_desactivar_robot()
        elif opcion_elegida == 2:
            respuesta = self.activar_desactivar_motores()
        elif opcion_elegida == 3:
            respuesta = self.seleccionar_modo_trabajo()
        elif opcion_elegida == 4:
            respuesta = self.seleccionar_modo_coordenadas()
        elif opcion_elegida == 5:
            self.mostrar_operaciones_cliente()
        elif opcion_elegida == 6:
            self.escribir_comando()
        elif opcion_elegida == 7:
            self.mostrar_reporte_general()
        elif opcion_elegida == 8:
            self.mostrar_log_trabajo()
        elif opcion_elegida == 9:
            self.mostrar_usuarios()
        elif opcion_elegida == 10:
            self.modificar_parametros_conexion()
        elif opcion_elegida == 11:
            if not self.servidor.get_estado_servidor():
                self.servidor.iniciar_servidor()
            else:
                self.servidor.apagar_servidor()
        elif opcion_elegida == 12:
            self.servidor.cerrar_sesion()
        elif opcion_elegida == 13:
            self.listar_comandos()
        elif opcion_elegida == 14:
            return 14
        else:
            print("Opción no válida.")
        
        # Retornar respuesta (sirve para el cliente practicamente):
        if respuesta not in None:
            return respuesta
        
        opcion_elegida = None

    # Métodos adicionales para manipular el robot y mostrar reportes
    def activar_desactivar_robot(self):
        if self.controlador.get_estado_robot():
            respuesta = self.controlador.desconectar_robot()
            self.peticion = "Desconectar robot"
        else:
            respuesta = self.controlador.conectar_robot()
            self.peticion = "Conectar robot"
        return respuesta

    def activar_desactivar_motores(self):
        if self.controlador.get_estado_motores():
            respuesta = self.controlador.desactivar_motores()  # Usamos la instancia
            self.peticion = "Desactivar motores"
        else:
            respuesta = self.controlador.activar_motores()
            self.peticion = "Activar motores"
        return respuesta

    def mostrar_reporte_general(self):
        Archivo.mostrar_info()  # Muestra información general
        self.peticion = "Mostrar reporte general"

    def mostrar_log_trabajo(self):
        self.peticion= "Mostrar log de trabajo"
        self.sesion = self.servidor.get_sesion()
        self.usuarios = self.servidor.get_usuarios()
        if self.sesion and 'nombre_usuario' in self.sesion:
            nombre_usuario = self.sesion['nombre_usuario']
            # Verificamos si el usuario tiene permisos de administrador
            for usuario in self.usuarios:
                if usuario.nombre_usuario == nombre_usuario and usuario.admin:
                    LogTrabajo.leer_CSV()
                    return
            print("Acceso denegado. Solo los administradores pueden ver la lista de usuarios.")
        else:
            print("No hay ningún usuario en sesión.")

    def seleccionar_modo_trabajo(self):
        if self.modo_trabajo == "manual":
            self.modo_trabajo = "automatico"
            self.peticion = "Seleccionar modo automatico"
        elif self.modo_trabajo == "automatico":
            self.modo_trabajo = "manual"
            self.peticion = "Seleccionado modo manual"
        respuesta = f"Modo de trabajo seleccionado: {self.modo_trabajo}"
        print(respuesta)
        return respuesta

    def seleccionar_modo_coordenadas(self):
        if self.modo_coordenadas == "absolutas":
            self.modo_coordenadas = "relativas"
            respuesta = self.controlador.enviar_comando('G91')
            self.peticion = "Seleccionar modo de coordenadas relativas"
        elif self.modo_coordenadas == "relativas":
            self.modo_coordenadas = "absolutas"
            respuesta = self.controlador.enviar_comando('G90')
            self.peticion = "Seleccionar modo de coordenadas absolutas"
        return respuesta

    def mostrar_usuarios(self):
        self.peticion= "Mostrar usuarios"
        self.sesion = self.servidor.get_sesion()
        self.usuarios = self.servidor.get_usuarios()
        if self.sesion and 'nombre_usuario' in self.sesion:
            nombre_usuario = self.sesion['nombre_usuario']
            # Verificamos si el usuario tiene permisos de administrador
            for usuario in self.usuarios:
                if usuario.nombre_usuario == nombre_usuario and usuario.admin:
                    print("Usuarios registrados:")
                    for u in self.usuarios:
                        print(u.nombre_usuario)  # Muestra el nombre del usuario
                    return
            print("Acceso denegado. Solo los administradores pueden ver la lista de usuarios.")
        else:
            print("No hay ningún usuario en sesión.")

    def modificar_parametros_conexion(self):
        self.peticion = "Modificar parametros de conexion"
        try:
            puerto_COM = input('Ingrese el nuevo puerto de COM al que se quiere conectar: ')
            baudrate = int(input('Ingrese la velocidad de comunicacion (baudrate): '))
            self.controlador.cambiar_parametros_comunicacion(baudrate, puerto_COM)
            self.controlador.conectar_robot()
        except Exception as e:
            print(f"Error al modificar los parámetros de conexión: {e}")

    def mostrar_operaciones_cliente(self):
        print("Operaciones posibles a realizar por un cliente o por un operador en el servidor: \n")
        print(" M3: Activar gripper \n")
        print(" M5: Desactivar gripper \n")
        print(" G28: Hacer homing \n")
        print(" G1: Hacer un movimiento a una determinada posición \n")
        print(" (Para enviar este comando, realizar lo siguiente: [G1 Xa Yb Zc], donde Xa, Yb y Zc son las posiciones a las que se debe mover.)")
        print(" M114: Reporte de modo de coordenadas y posición actual \n")
        print(" G90: Modo de coordenadas absolutas \n")
        print(" G91: Modo de coordenadas relativas \n")
        print(" M17: Activar motores \n")
        print(" M18: Desactivar motores \n")        

    def escribir_comando(self):
        self.peticion = "Enviar comando"
        if self.modo_trabajo == "manual":
            try: 
                comando = input("Ingrese el comando en G-Code para accionar el robot: ")
                self.controlador.enviar_comando(comando)
            except Exception as e:
                print(f"Error al enviar el comando: {e} ")
        else: 
            print("El modo de trabajo no es manual. Por favor, cambie el modo de trabajo antes de realizar esta accion.")
