class Usuario:

    def __init__(self, nombre_usuario, contrasena, admin = False, token = None):
        self.nombre_usuario = nombre_usuario
        self.contrasena = contrasena
        self.admin = admin
        self.token = token

    def crear_usuario(self, nombre_usuario, contrasena, admin=False):
        nuevo_usuario = Usuario(nombre_usuario, contrasena, admin)
        self.usuarios.append(nuevo_usuario)
        nuevo_usuario.guardar_usuarios_csv()
    






