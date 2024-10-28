from archivo import Archivo
from logTrabajo import LogTrabajo
from servidor import Servidor
from controlador import Controlador
import time


class InterfazServidor:

    def __init__(self, modo_trabajo = "automatico", modo_coordenadas = "absolutas"):
        self.modo_trabajo = modo_trabajo
        self.controlador = Controlador()  # Instancia de Controlador
        self.servidor = Servidor()  # Instancia de Servidor
        self.modo_coordenadas = modo_coordenadas
        self.usuario = None
        self.peticion = None
        self.ip_cliente = None

    def iniciar_sesion_usuario(self):
        print(f"Sesion iniciada por el usuario: {self.usuario} con la IP: {self.IP}")	


    def listar_comandos(self):
        print("Comandos posibles a realizar: \n")
        print(" 1) Conectar/desconectar robot. \n")
        print(" 2) Activar/desactivar motores del robot. \n")
        print(" 3) Mostrar reporte de informacion general. \n")
        print(" 4) [SOLO ADMIN] Mostrar reporte de log de trabajo del servidor. \n")
        print(" 5) Seleccionar los modos de trabajo (manual o automatico) o coordenadas (absolutas o relativas). \n")
        print(" 6) [SOLO ADMIN] Mostrar usuarios. \n")
        print(" 7) [SOLO ADMIN] Mostrar/editar los parametros de conexion del robot. \n")
        print(" 8) [SOLO ADMIN] Encender/apagar servidor. \n")
        print(" 9) Mostrar operaciones posibles a realizar por un cliente o un operador en el servidor. \n")
        print(" 10) [SOLO MODO MANUAL] Enviar comandos en formato G-Code para accionar robot. ")

    def administrar_comandos(self):
        opcion_elegida = None
        while opcion_elegida not in list(range(1, 10)):
            try:
                opcion_elegida = int(input("Ingrese la acción a realizar: "))
                inicio = time.time()

                if opcion_elegida == 1:
                    self.activar_desactivar_robot()
                elif opcion_elegida == 2:
                    self.activar_desactivar_motores()
                elif opcion_elegida == 3:
                    self.mostrar_reporte_general()
                elif opcion_elegida == 4:
                    self.mostrar_log_trabajo()
                elif opcion_elegida == 5:
                    cambio_a_realizar = None
                    while cambio_a_realizar not in [1, 2]:
                        try:
                            cambio_a_realizar = int(input("Desea cambiar el modo de trabajo [1] o el modo de coordenadas [2]?: "))
                            if cambio_a_realizar == 1:
                                self.seleccionar_modo_trabajo()
                            elif cambio_a_realizar == 2:
                                self.seleccionar_modo_coordenadas()
                        except ValueError:
                            print("Por favor, ingrese un número válido.")
                elif opcion_elegida == 6:
                    self.mostrar_usuarios()
                elif opcion_elegida == 7:
                    self.modificar_parametros_conexion()
                elif opcion_elegida == 8:
                    estado_servidor = self.servidor.get_estado_servidor()  # Usamos la instancia
                    if estado_servidor:
                        self.servidor.apagar_servidor()
                    else:
                        self.servidor.iniciar_servidor()
                elif opcion_elegida == 9:
                    self.mostrar_operaciones_cliente()
                elif opcion_elegida == 10:
                    self.escribir_comando()
                else:
                    print("Opción no válida.")
            except ValueError:
                print("Por favor, ingrese un número válido.")
                peticion = None
                if peticion:
                    fin = time.time()
                    tiempo_ejecucion = fin - inicio

                    '''''''''
                    LogTrabajo(peticiones=peticion, usuario = self.usuario, fallos = 0, exitos = 1, tiempo_ejecucion=tiempo_ejecucion, IP=self)
                    '''
    
    def activar_desactivar_robot(self):
        if self.controlador.get_estado_robot():  # Usamos la instancia
            self.controlador.desconectar_robot()
            self.peticion = "Desconectar robot"
        else:
            self.controlador.conectar_robot()
            self.peticion = "Conectar robot"

    def activar_desactivar_motores(self):
        if self.controlador.get_estado_motores():
            self.controlador.desactivar_motores()  # Usamos la instancia
            self.peticion = "Desactivar motores"
        else:
            self.controlador.activar_motores()
            self.peticion = "Activar motores"

    def mostrar_reporte_general(self):
        Archivo.mostrar_info()  # Muestra información general
        self.peticion= "Mostrar reporte general"

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
        self.modo_trabajo = None
        while self.modo_trabajo not in ["manual", "automatico"]:  # Lista para validar los modos
            self.modo_trabajo = input("Ingrese: manual/automatico: ").lower()  # Convertir a minúsculas
            if self.modo_trabajo == "manual":
                self.peticion = "Seleccionar modo manual"
            if self.modo_trabajo == "automatico":
                self.peticion = "Seleccionar modo automatico"
        print(f"Modo de trabajo seleccionado: {self.modo_trabajo}")

    def seleccionar_modo_coordenadas(self):
        self.modo_coordenadas = None
        while self.modo_coordenadas not in ["absolutas", "relativas"]:
            self.modo_coordenadas = input("Ingrese: absolutas/relativas: ").lower()
        print(f"Modo de coordenadas seleccionado: {self.modo_coordenadas}")
        if self.modo_coordenadas == "absolutas":
            self.controlador.enviar_comando('G90')
            self.peticion = "Seleccionar modo de coordenadas absolutas"
        elif self.modo_coordenadas == "relativas":
            self.controlador.enviar_comando('G91')
            self.peticion = "Seleccionar modo de coordenadas relativas"

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

'''

    def set_ip_cliente(self):
        self.ip_cliente = self.servidor.get_"

    '''
    


        
