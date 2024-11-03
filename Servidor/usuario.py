import csv

class Usuario:

    def __init__(self, nombre_usuario, contrasena, admin = False):
        self.nombre_usuario = nombre_usuario
        self.contrasena = contrasena
        self.admin = admin

    def crear_usuario(self, nombre_usuario, contrasena, admin=False):
        nuevo_usuario = Usuario(nombre_usuario, contrasena, admin)
        self.usuarios.append(nuevo_usuario)
        nuevo_usuario.guardar_usuarios_csv()

    # def guardar_usuarios_csv(self, archivo='usuarios_servidor.csv'):
    #     try:
    #         with open(archivo, mode='a', newline='') as csvfile:
    #             writer = csv.writer(csvfile)

    #             writer.writerow([
    #                 self.nombre_usuario,
    #                 self.contrasena,
    #                 self.admin
    #                 ])
                
    #     except Exception as e:
    #         print(f"Error al escribir el usuario: {e}")

    






