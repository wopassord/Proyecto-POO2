from fastapi import FastAPI, Form, UploadFile, File, HTTPException, Query, Cookie
from fastapi.responses import HTMLResponse
import uvicorn
from starlette.responses import FileResponse, RedirectResponse
import os
from interprete_gcode import UtilGcode
from auth import GestionUsuarios
import csv
from controlador import Controlador
from LogTrabajo1 import LogTrabajo


app = FastAPI()
gcode_interprete = UtilGcode()
auth = GestionUsuarios()
token_dict = {}  # Diccionario para almacenar los tokens de sesión
controlador = Controlador()
log_trabajo = LogTrabajo(servidor=controlador)


def protect_route(token):
    if not auth.find_token(token):
        raise HTTPException(status_code=401, detail="Acceso no autorizado")

    return

# Cargar el archivo HTML como plantilla
def load_html_template(archivo):
    # Verifica solo una referencia a "Servidor"
    template_path = os.path.abspath(os.path.join("interfaz_web", archivo))
    print(
        "Ruta de la plantilla HTML:", template_path
    )  # Verifica que el path sea correcto
    try:
        with open(template_path, "r", encoding="ISO-8859-1") as f:
            return f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Plantilla HTML no encontrada")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al cargar la plantilla HTML: {str(e)}"
        )


@app.get("/")
async def index_page():
    # Define el directorio base usando `__file__` para apuntar a la raíz del proyecto
    base_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )  # Esto sube un nivel

    # Construye la ruta de `index.html` correctamente desde `base_dir`
    html_path = os.path.join(base_dir, "Servidor", "interfaz_web", "index.html")
    print("Directorio actual:", os.getcwd())
    print("Ruta completa del archivo index.html:", html_path)

    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return {"error": f"Archivo index.html no encontrado en {html_path}"}


# Ruta para mostrar el formulario de inicio de sesión
@app.get("/login")
async def login_form():
    # Usa `base_dir` para la ruta base del proyecto
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Construye la ruta hacia `login.html`
    html_path = os.path.join(base_dir, "Servidor", "interfaz_web", "login.html")
    print("Ruta completa del archivo login.html:", html_path)

    if os.path.exists(html_path):
        return FileResponse(html_path)
    else:
        return {"error": f"Archivo login.html no encontrado en {html_path}"}


# Ruta para procesar el inicio de sesión
@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    data = auth.verificar_usuario(username, password)
    if data is None:
        data = auth.registrar_usuario(username, password)
        exito = 1
        accion = "Registro e Inicio de Sesion"
    else:
        exito = 1
        accion = "Inicio de Sesion"

    # Actualizar el log con la acción de inicio de sesión
    log_trabajo.actualizar_log(
        peticion=accion,
        usuario=username,
        fallos=0 if exito else 1,
        exitos=1 if exito else 0,
        tiempo_ejecucion=0.0,  # Puedes calcular el tiempo si es necesario
    )
    log_trabajo.escribir_CSV()  # Escribir en el log inmediatamente

    # Crear la respuesta de redirección después del login exitoso
    response = RedirectResponse(url="/menu", status_code=303)
    response.set_cookie(key="token", value=data[3])
    return response


# Ruta para mostrar el menú después del login
@app.get("/menu")
async def menu_page(token: str = Cookie(None)):
    protect_route(token)
    menu_template = load_html_template("menu.html")
    user = auth.find_user(token)
    username = user[0]

    # Verificar el valor booleano del usuario logueado para mostrar o no la opción de log
    show_log_option = (
        user[2] == "True"
    )  # Asegúrate de que el valor booleano esté en el índice 2 como "True" o "False"
    log_option_html = ""
    if show_log_option:
        log_option_html = "<div class='card' onclick=\"location.href='/log_trabajo'\"><div class='card-title'>Ver Log de Trabajo</div></div>"

    # Inserta la opción del log en el menú si corresponde
    html_content = menu_template.replace("{{ log_option }}", log_option_html)
    html_content = html_content.replace("{{ username }}", username)
    return HTMLResponse(content=html_content)


@app.get("/listar-usuarios")
async def listar_usuarios(token: str = Cookie(None)):
    protect_route(token)

    # Verificar el usuario logueado y su valor booleano
    usuario_logueado = auth.find_user(token)
    if usuario_logueado is None:
        raise HTTPException(status_code=401, detail="Usuario no autorizado")

    mostrar_password = (
        usuario_logueado[2] == "True"
    )  # Asumimos que el booleano está en la posición 2 como string

    usuarios = []
    with open(auth.archivo_csv, mode="r") as file:
        reader = csv.reader(file)
        for row in reader:
            if mostrar_password:
                # Mostrar tanto el nombre como la contraseña
                usuarios.append(f"<div class='usuario'>{row[0]} - {row[1]}</div>")
            else:
                # Mostrar solo el nombre
                usuarios.append(f"<div class='usuario'>{row[0]}</div>")

    # Cargar la plantilla HTML y reemplazar el contenido de usuarios
    usuarios_template = load_html_template("listar_usuarios.html")
    usuarios_html = "".join(usuarios)
    html_content = usuarios_template.replace("{{ usuarios }}", usuarios_html)

    return HTMLResponse(content=html_content)


@app.get("/log_trabajo")
async def log_trabajo_route(token: str = Cookie(None)):
    protect_route(token)

    # Leer el log CSV y almacenar las filas para el HTML
    rows = []
    with open(
        "log_trabajo.csv", mode="r", encoding="ISO-8859-1"
    ) as csvfile:  # Añadir encoding
        reader = csv.reader(csvfile)
        headers = next(reader)  # Leer cabeceras
        for row in reader:
            rows.append(row)

    # Generar el HTML para la tabla de log
    log_template = load_html_template("log_trabajo.html")
    headers_html = "".join(f"<th>{header}</th>" for header in headers)
    rows_html = "".join(
        "<tr>" + "".join(f"<td>{col}</td>" for col in row) + "</tr>" for row in rows
    )
    table_html = f"<table class='log-table'><thead><tr>{headers_html}</tr></thead><tbody>{rows_html}</tbody></table>"

    html_content = log_template.replace("{{ log_table }}", table_html)

    return HTMLResponse(content=html_content)


# Ruta para conectar o desconectar el robot
@app.get("/on_off_robot")
async def on_off_robot(token: str = Cookie(None)):
    protect_route(token)
    user = auth.find_user(token)[0]

    # Alternar el estado de conexión del robot
    if controlador.get_estado_robot():
        mensaje, exito = controlador.desconectar_robot()
        accion = "Desconectar Robot"
    else:
        mensaje, exito = controlador.conectar_robot()
        accion = "Conectar Robot"

    # Formatear el mensaje para mostrar el estado
    mensaje = f"{mensaje} de manera exitosa, {user}."

    log_trabajo.actualizar_log(
        peticion=accion,
        usuario=user,
        fallos=0 if exito else 1,
        exitos=1 if exito else 0,
        tiempo_ejecucion=0.0,  # Puedes ajustar el tiempo si es relevante
    )
    log_trabajo.escribir_CSV()

    # Cargar la plantilla y reemplazar el mensaje
    robot_template = load_html_template("on_off_robot.html")
    html_content = robot_template.replace("{{ mensaje }}", mensaje)

    return HTMLResponse(content=html_content)


# Ruta para controlar motores
@app.get("/motores")
async def motores(token: str = Cookie(None)):
    protect_route(token)
    user = auth.find_user(token)[0]

    # Alternar el estado de los motores
    if controlador.get_estado_motores():
        mensaje, exito = controlador.desactivar_motores()
        accion = "Desactivar Motores"
    else:
        mensaje, exito = controlador.activar_motores()
        accion = "Activar Motores"

    # Formatear el mensaje para mostrar el estado
    mensaje = f"{mensaje} correctamente, {user}."

    log_trabajo.actualizar_log(
        peticion=accion,
        usuario=user,
        fallos=0 if exito else 1,
        exitos=1 if exito else 0,
        tiempo_ejecucion=0.0,  # Ajusta si se calcula el tiempo
    )
    log_trabajo.escribir_CSV()

    # Cargar la plantilla y reemplazar el mensaje
    motores_template = load_html_template("motores.html")
    html_content = motores_template.replace("{{ mensaje }}", mensaje)

    return HTMLResponse(content=html_content)


@app.get("/dashboard")
async def dashboard(token: str = Cookie(None)):
    protect_route(token)

    dashboard_template = load_html_template("dashboard.html")
    user = auth.find_user(token)
    html_content = dashboard_template.replace("{{ username }}", user[0])
    return HTMLResponse(content=html_content)


@app.post("/carga-gcode")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Leer el contenido del archivo
        file_content = await file.read()
        file_content_str = file_content.decode("latin-1")  # Decodificar a string
        image_path = gcode_interprete.subir_archivo_gcode(
            file.filename, file_content_str, True
        )
        if image_path is None:
            raise ValueError("Error al generar la imagen")

        # Extraer el nombre del archivo de imagen desde el path
        image_name = os.path.basename(image_path)

        # Redireccionar a `/ver-imagen` con el nombre de la imagen
        return RedirectResponse(f"/ver-imagen?image={image_name}", status_code=303)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ver-imagen")
async def ver_imagen(image: str = Query(...)):
    # Define el directorio donde están almacenadas las imágenes
    base_dir = os.path.abspath("Servidor/imagenes")
    image_path = os.path.join(base_dir, image)

    # Verificar que el archivo existe antes de procesar la respuesta
    if not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    # Cargar el contenido de la plantilla HTML
    html_template = load_html_template("ver_imagen.html")
    # Reemplazar la variable en la plantilla por la ruta de la imagen
    html_content = html_template.replace("{{ image_path }}", f"/imagenes/{image}")

    return HTMLResponse(content=html_content)


@app.get("/imagenes/{path}")
async def get_image(path: str):
    base_dir = os.path.abspath("Servidor/imagenes")
    image_path = os.path.join(base_dir, path)

    # Verificar que el archivo existe antes de enviarlo
    if not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

    # Enviar el archivo como respuesta
    return FileResponse(image_path, media_type="image/png")


if __name__ == "__main__":
    print("Iniciando servidor web...")
    uvicorn.run(app, host="127.0.0.1", port=3000)
